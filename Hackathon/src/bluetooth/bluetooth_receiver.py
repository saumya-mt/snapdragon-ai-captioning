import os
from Hackathon.src.models.image_captioning import generate_caption_with_blip
from vqa_handler import VQAHandler
from accessibility_handler import AccessibilityHandler
from gtts import gTTS
import time

class ImageProcessor:
    def __init__(self):
        print("Initializing models...")
        self.vqa_handler = VQAHandler()
        self.accessibility_handler = AccessibilityHandler()
        
        # Create directories if they don't exist
        os.makedirs("received_images", exist_ok=True)
        os.makedirs("audio_output", exist_ok=True)
        
        # Directory to watch for new images
        self.watch_dir = "received_images"
        
    def process_image(self, image_path):
        """Process received image and generate description"""
        try:
            print(f"\nProcessing image: {image_path}")
            
            # Generate caption
            print("Generating caption...")
            caption = generate_caption_with_blip(image_path)
            print(f"Caption: {caption}")
            
            # Get scene information
            print("Detecting scene...")
            try:
                scene_type, scene_confidence = self.accessibility_handler.detect_scene(image_path)
                scene_info = f"It appears to be a {scene_type} scene. "
                print(f"Scene: {scene_type} (Confidence: {scene_confidence:.2%})")
            except Exception as e:
                print(f"Scene detection error: {e}")
                scene_info = ""
            
            # Generate VQA responses
            print("Analyzing image details...")
            questions = [
                "What is the main subject?",
                "What colors are present?",
                "Is this indoors or outdoors?"
            ]
            
            vqa_results = []
            for question in questions:
                try:
                    result = self.vqa_handler.get_answer(image_path, question)
                    if isinstance(result, dict) and 'answer' in result:
                        answer = result['answer']
                        vqa_results.append(f"{answer}")
                        print(f"Q: {question}")
                        print(f"A: {answer}")
                except Exception as e:
                    print(f"VQA error for question '{question}': {e}")
            
            # Generate detailed description
            description = f"This image shows {caption}. {scene_info}"
            if vqa_results:
                description += " ".join(vqa_results) + "."
            
            print("\nFull description:")
            print(description)
            
            # Generate audio
            audio_path = os.path.join("audio_output", f"description_{int(time.time())}.mp3")
            print(f"\nGenerating audio description: {audio_path}")
            tts = gTTS(text=description, lang='en')
            tts.save(audio_path)
            
            print("\nProcessing complete!")
            print(f"Audio file saved to: {audio_path}")
            
            return {
                'caption': caption,
                'description': description,
                'audio_path': audio_path
            }
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return None

    def watch_for_images(self):
        """Watch for new images in the received_images directory"""
        print(f"\nWatching for images in: {self.watch_dir}")
        print("Transfer an image from your phone to this directory...")
        
        # Keep track of processed files
        processed_files = set()
        
        while True:
            try:
                # Check for new images
                current_files = set(os.listdir(self.watch_dir))
                new_files = current_files - processed_files
                
                for filename in new_files:
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(self.watch_dir, filename)
                        print(f"\nNew image detected: {filename}")
                        
                        # Process the image
                        result = self.process_image(image_path)
                        
                        if result:
                            print("\n=== Results ===")
                            print(f"Caption: {result['caption']}")
                            print(f"Audio saved to: {result['audio_path']}")
                            print("================")
                        
                        # Add to processed files
                        processed_files.add(filename)
                
                time.sleep(1)  # Check every second
                
            except KeyboardInterrupt:
                print("\nStopping image watch...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    processor = ImageProcessor()
    processor.watch_for_images() 