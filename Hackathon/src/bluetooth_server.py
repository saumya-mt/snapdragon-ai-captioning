import asyncio
from bleak import BleakScanner, BleakClient
import os
from image_captioning import generate_caption_with_blip
from vqa_handler import VQAHandler
from accessibility_handler import AccessibilityHandler
from gtts import gTTS

class BluetoothServer:
    def __init__(self):
        self.vqa_handler = VQAHandler()
        self.accessibility_handler = AccessibilityHandler()
        self.received_data = bytearray()
        
        # Create directories if they don't exist
        os.makedirs("received_images", exist_ok=True)
        os.makedirs("audio_output", exist_ok=True)

    async def start_server(self):
        print("Starting Bluetooth server...")
        print("Waiting for mobile device connection...")
        
        while True:
            try:
                # Scan for devices
                devices = await BleakScanner.discover()
                for device in devices:
                    if device.name == "Saumya":  # Replace with your phone's name
                        print(f"Found device: {device.name}")
                        await self.connect_to_device(device)
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)

    async def connect_to_device(self, device):
        print(f"Connecting to {device.name}...")
        client = BleakClient(device.address)
        
        try:
            await client.connect()
            print("Connected! Waiting for image...")
            
            # Set up notification handler
            await client.start_notify(
                "image_characteristic_uuid",  # You'll need to replace this with your phone's characteristic UUID
                self.handle_image_data
            )
            
            # Keep connection alive
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            await client.disconnect()

    async def handle_image_data(self, sender, data):
        try:
            # Accumulate received data
            self.received_data.extend(data)
            
            # Check if this is the end of the image
            if len(data) < 512:  # Assuming smaller packet means end of transmission
                # Save received image
                image_path = "received_images/received_image.jpg"
                with open(image_path, "wb") as f:
                    f.write(self.received_data)
                
                print("Image received! Processing...")
                
                # Process image using your existing models
                results = await self.process_image(image_path)
                
                # Generate audio response
                audio_path = self.text_to_speech(results['description'])
                
                # Send audio back
                with open(audio_path, "rb") as f:
                    audio_data = f.read()
                    await sender.write_gatt_char(
                        "audio_characteristic_uuid",  # Replace with your characteristic UUID
                        audio_data
                    )
                
                print("Processed and sent response!")
                
                # Clear received data for next image
                self.received_data = bytearray()
                
        except Exception as e:
            print(f"Error processing data: {e}")
            self.received_data = bytearray()

    async def process_image(self, image_path):
        """Process the received image using your existing models"""
        try:
            # Generate caption
            caption = generate_caption_with_blip(image_path)
            
            # Get scene information
            scene_type, scene_confidence = self.accessibility_handler.detect_scene(image_path)
            
            # Get some basic VQA information
            questions = [
                "What is the main subject?",
                "What colors are present?",
                "Is this indoors or outdoors?"
            ]
            
            vqa_results = {}
            for question in questions:
                result = self.vqa_handler.get_answer(image_path, question)
                vqa_results[question] = result['answer']
            
            # Generate detailed description
            description = f"This image shows {caption}. "
            description += f"It appears to be a {scene_type} scene. "
            for q, a in vqa_results.items():
                description += f"{a}. "
            
            return {
                'caption': caption,
                'description': description,
                'scene_info': (scene_type, scene_confidence),
                'vqa_results': vqa_results
            }
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def text_to_speech(self, text):
        """Convert description to speech"""
        try:
            audio_path = "audio_output/response.mp3"
            tts = gTTS(text=text, lang='en')
            tts.save(audio_path)
            return audio_path
        except Exception as e:
            print(f"Error generating speech: {e}")
            return None

async def main():
    server = BluetoothServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main()) 