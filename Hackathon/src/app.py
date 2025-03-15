import chainlit as cl
from PIL import Image
from image_captioning import generate_caption_with_blip
from vqa_handler import VQAHandler
import tempfile
import os
from optimized_models import OptimizedModelHandler
from accessibility_handler import AccessibilityHandler
import asyncio
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from gtts import gTTS

# Initialize VQA handler globally
vqa_handler = VQAHandler()

# Initialize handlers globally
model_handler = OptimizedModelHandler()
accessibility_handler = AccessibilityHandler()

# Initialize models and handlers
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_audio(text, lang='en'):
    """Generate audio from text using gTTS"""
    tts = gTTS(text=text, lang=lang)
    # Create temporary file for audio
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts.save(fp.name)
        return fp.name

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    await cl.Message(
        content="Welcome! This is an accessible image analysis system.\n"
                "You can:\n"
                "1. Upload an image for analysis\n"
                "2. Ask questions by typing or voice\n"
                "3. Receive audio descriptions\n"
                "\nPress 'V' to use voice input."
    ).send()
    
    # Initialize session variables
    cl.user_session.set("current_image_path", None)
    cl.user_session.set("accessibility_mode", True)

@cl.on_message
async def main(message: cl.Message):
    """Handle incoming messages and image processing"""
    
    accessibility_mode = cl.user_session.get("accessibility_mode", True)
    current_image_path = cl.user_session.get("current_image_path")
    
    if message.elements:
        image_element = message.elements[0]
        image_path = image_element.path
        cl.user_session.set("current_image_path", image_path)
        
        try:
            # Generate basic caption
            caption = model_handler.generate_caption(image_path)
            
            # Get scene information
            scene_type, scene_confidence = accessibility_handler.detect_scene(image_path)
            
            # Generate initial VQA results for key aspects
            initial_questions = [
                "What is in the foreground?",
                "What is in the background?",
                "What are the main colors?",
                "Is it indoor or outdoor?",
                "What is the lighting like?"
            ]
            
            vqa_results = {}
            for question in initial_questions:
                result = model_handler.answer_question(image_path, question)
                vqa_results[question] = result
            
            # Generate detailed description
            detailed_description = accessibility_handler.generate_detailed_description(
                caption, (scene_type, scene_confidence), vqa_results
            )
            
            # Convert description to speech
            audio_path = accessibility_handler.text_to_speech(detailed_description)
            
            # Send response with both text and audio
            await cl.Message(
                content=f"Detailed Description:\n{detailed_description}",
                elements=[
                    cl.Image(name="uploaded_image", display="inline", path=image_path),
                    cl.Audio(name="description_audio", path=audio_path)
                ]
            ).send()
            
        except Exception as e:
            await cl.Message(content=f"Error processing image: {str(e)}").send()
        return

    # Handle voice input
    if message.content.lower() == "v":
        try:
            question = accessibility_handler.listen_for_question()
            message.content = question  # Update message content with transcribed question
        except Exception as e:
            await cl.Message(content=f"Error processing voice input: {str(e)}").send()
            return

    # Process questions
    if current_image_path:
        try:
            result = model_handler.answer_question(current_image_path, message.content)
            response = f"Q: {message.content}\nA: {result['answer']}"
            
            # Convert answer to speech
            audio_path = accessibility_handler.text_to_speech(
                f"You asked: {message.content}. The answer is: {result['answer']}"
            )
            
            await cl.Message(
                content=response,
                elements=[
                    cl.Image(name="reference_image", path=current_image_path),
                    cl.Audio(name="answer_audio", path=audio_path)
                ]
            ).send()
            
        except Exception as e:
            await cl.Message(content=f"Error: {str(e)}").send()
    else:
        await cl.Message(content="Please upload an image first.").send()

@cl.action_callback("ask_question")
async def on_action(action):
    """Handle action button clicks"""
    question = action.payload["question"]
    
    # Get current image path from session
    current_image_path = cl.user_session.get("current_image_path")
    
    if current_image_path is None:
        await cl.Message(content="Please upload an image first before asking questions.").send()
        return
    
    try:
        # Process the question using VQA
        result = vqa_handler.get_answer(current_image_path, question)
        
        # Send response with the image
        await cl.Message(
            content=f"Q: {question}\nA: {result['main_answer']} (Confidence: {result['confidence']})",
            elements=[
                cl.Image(name="reference_image", 
                        display="inline", 
                        path=current_image_path)
            ]
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"Error processing question: {str(e)}"
        ).send()

if __name__ == "__main__":
    cl.run()

