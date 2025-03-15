import bluetooth
import threading
from Hackathon.src.models.image_captioning import generate_caption_with_blip
from vqa_handler import VQAHandler
from Hackathon.handlers.accessibility_handler import AccessibilityHandler
from gtts import gTTS
import os

class AccessibleImageServer:
    def __init__(self):
        self.vqa_handler = VQAHandler()
        self.accessibility_handler = AccessibilityHandler()
        
        # Create output directories
        os.makedirs("received_images", exist_ok=True)
        os.makedirs("audio_output", exist_ok=True)
        
        # Initialize Bluetooth server
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_socket.bind(("", bluetooth.PORT_ANY))
        self.server_socket.listen(1)
        
        # Get the port number
        self.port = self.server_socket.getsockname()[1]
        
        # Start advertising service
        bluetooth.advertise_service(
            self.server_socket, "ImageAnalysisServer",
            service_id="image_analysis_service",
            service_classes=[bluetooth.SERIAL_PORT_CLASS],
            profiles=[bluetooth.SERIAL_PORT_PROFILE]
        )
        
        print(f"Server started on port {self.port}")
        print("Waiting for connections...")
    
    def process_image(self, image_path):
        """Process image and generate detailed description"""
        try:
            # Generate caption
            caption = generate_caption_with_blip(image_path)
            
            # Get scene information
            scene_type, confidence = self.accessibility_handler.detect_scene(image_path)
            
            # Get important details through VQA
            questions = [
                "What is in the foreground?",
                "Are there any people?",
                "What objects are visible?",
                "What colors are prominent?",
                "Is it indoor or outdoor?",
                "What is the lighting like?",
                "Are there any potential obstacles or hazards?"
            ]
            
            details = []
            for question in questions:
                result = self.vqa_handler.get_answer(image_path, question)
                if result and 'answer' in result:
                    details.append(f"{question} {result['answer']}")
            
            # Create detailed, accessibility-focused description
            description = f"I see {caption}. "
            description += f"This appears to be a {scene_type} scene. "
            description += " ".join(details)
            
            # Generate audio file
            audio_path = os.path.join("audio_output", "description.mp3")
            tts = gTTS(text=description, lang='en')
            tts.save(audio_path)
            
            return audio_path, description
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return None, str(e)
    
    def handle_client(self, client_socket):
        """Handle client connection"""
        try:
            while True:
                # Receive image size
                size_data = client_socket.recv(8)
                if not size_data:
                    break
                    
                image_size = int.from_bytes(size_data, 'big')
                
                # Receive image data
                image_data = b''
                while len(image_data) < image_size:
                    chunk = client_socket.recv(min(4096, image_size - len(image_data)))
                    if not chunk:
                        break
                    image_data += chunk
                
                # Save received image
                image_path = os.path.join("received_images", "temp_image.jpg")
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                
                print("Image received, processing...")
                
                # Process image
                audio_path, description = self.process_image(image_path)
                
                if audio_path:
                    # Send audio file
                    with open(audio_path, 'rb') as f:
                        audio_data = f.read()
                    
                    # Send audio size first
                    client_socket.send(len(audio_data).to_bytes(8, 'big'))
                    
                    # Send audio data
                    client_socket.send(audio_data)
                    
                    print("Processed and sent response")
                    print(f"Description: {description}")
                
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
    
    def start(self):
        """Start the server"""
        while True:
            try:
                client_socket, client_info = self.server_socket.accept()
                print(f"Accepted connection from {client_info}")
                
                # Handle client in a new thread
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket,)
                )
                client_thread.start()
                
            except Exception as e:
                print(f"Error accepting connection: {e}")
                break
        
        self.server_socket.close()

if __name__ == "__main__":
    server = AccessibleImageServer()
    server.start() 