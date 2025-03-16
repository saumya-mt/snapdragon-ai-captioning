#accessibility_handler.py

 
from transformers import pipeline
import edge_tts
import os
import asyncio
 
class AccessibilityHandler:
    def __init__(self):
        # Initialize scene detection
        self.scene_detector = pipeline("image-classification", model="microsoft/resnet-50")
        
        # Create output directory for audio
        os.makedirs("audio_output", exist_ok=True)
        
        # Default voice for Edge TTS
        self.voice = "en-US-JennyNeural"
 
    async def text_to_speech(self, text, filename="response.mp3"):
        """Convert text to speech using Edge TTS"""
        try:
            audio_path = os.path.join("audio_output", filename)
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(audio_path)
            return audio_path
        except Exception as e:
            raise Exception(f"Error in text to speech conversion: {str(e)}")
 
    def detect_scene(self, image_path):
        """Detect the type of scene in the image"""
        try:
            results = self.scene_detector(image_path)
            return results[0]['label'], results[0]['score']
        except Exception as e:
            raise Exception(f"Error in scene detection: {str(e)}")
 
    def generate_detailed_description(self, caption, scene_info, vqa_results):
        """Generate a detailed, accessibility-focused description"""
        description = f"This image shows {caption}. "
        description += f"It appears to be a {scene_info[0]} scene with {scene_info[1]:.1%} confidence. "
        
        for question, result in vqa_results.items():
            if result and 'answer' in result:
                description += f"{question} {result['answer']}. "
                
        return description
 
    def change_voice(self, voice_name):
        """Change TTS voice"""
        self.voice = voice_name
 
