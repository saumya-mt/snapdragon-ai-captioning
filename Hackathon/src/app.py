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
import edge_tts  # Using Edge TTS

# Initialize Handlers & Models
vqa_handler = VQAHandler()
model_handler = OptimizedModelHandler()
accessibility_handler = AccessibilityHandler()
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", local_files_only=True) # can remove local_files_only if we want to connect to internet
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base", local_files_only=True)

async def generate_audio(text, lang='en'):
    """Generate audio from text using Edge TTS"""
    try:
        voice = "en-US-JennyNeural"  # Default voice
        communicate = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            await communicate.save(fp.name)
            return fp.name
    except Exception as e:
        print(f"⚠️ Error generating audio: {str(e)}")
        return None

@cl.on_chat_start
async def start():
    """Initialize the chat session"""
    await cl.Message(
        content="**🔍 Welcome to SnapSense!** 🖼️🔊\n\n"
                "SnapSense is an **accessible AI-powered image analysis assistant.**\n\n"
                "✨ **What You Can Do:**\n"
                "1️⃣ **Upload an Image** for AI-driven analysis.\n"
                "2️⃣ **Ask Questions** to learn more about the image.\n"
                "3️⃣ **Listen to Audio Descriptions** for accessibility.\n"
                "\n📷 **Try uploading an image to get started!**"
    ).send()
    
    # Initialize session variables
    cl.user_session.set("current_image_path", None)
    cl.user_session.set("accessibility_mode", True)

@cl.on_message
async def main(message: cl.Message):
    """Handle image uploads and Q&A interactions"""
    
    accessibility_mode = cl.user_session.get("accessibility_mode", True)
    current_image_path = cl.user_session.get("current_image_path")
    
    if message.elements:
        image_element = message.elements[0]
        image_path = image_element.path
        cl.user_session.set("current_image_path", image_path)
        
        try:
            caption = model_handler.generate_caption(image_path)
            scene_type, scene_confidence = accessibility_handler.detect_scene(image_path)

            initial_questions = [
                "What is in the foreground?",
                "What is in the background?",
                "What are the main colors?",
                "Is it indoor or outdoor?",
                "What is the lighting like?"
            ]

            vqa_results = {}
            for question in initial_questions:
                vqa_results[question] = model_handler.answer_question(image_path, question)

            detailed_description = accessibility_handler.generate_detailed_description(
                caption, (scene_type, scene_confidence), vqa_results
            )

            audio_path = await generate_audio(detailed_description)

            await cl.Message(
                content=f"**📝 Image Analysis:**\n{detailed_description}",
                elements=[
                    cl.Image(name="uploaded_image", display="inline", path=image_path),
                    cl.Audio(name="description_audio", path=audio_path)
                ]
            ).send()
            
        except Exception as e:
            await cl.Message(content=f"⚠️ Error processing image: {str(e)}").send()
        return

    if message.content.lower() == "v":
        try:
            question = accessibility_handler.listen_for_question()
            message.content = question  # Update message content with transcribed question
        except Exception as e:
            await cl.Message(content=f"🎙️ Error processing voice input: {str(e)}").send()
            return

    if current_image_path:
        try:
            result = model_handler.answer_question(current_image_path, message.content)
            response = f"**Q:** {message.content}\n**A:** {result['answer']}"

            audio_path = await generate_audio(
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
            await cl.Message(content=f"⚠️ Error: {str(e)}").send()
    else:
        await cl.Message(content="📷 **Please upload an image first before asking questions.**").send()

@cl.action_callback("ask_question")
async def on_action(action):
    """Handle action button clicks"""
    question = action.payload["question"]
    
    current_image_path = cl.user_session.get("current_image_path")
    
    if current_image_path is None:
        await cl.Message(content="📷 **Please upload an image first before asking questions.**").send()
        return
    
    try:
        result = vqa_handler.get_answer(current_image_path, question)

        audio_path = await generate_audio(
            f"Question: {question}. Answer: {result['main_answer']}"
        )

        await cl.Message(
            content=f"**Q:** {question}\n**A:** {result['main_answer']} (Confidence: {result['confidence']})",
            elements=[
                cl.Image(name="reference_image", display="inline", path=current_image_path),
                cl.Audio(name="answer_audio", path=audio_path)
            ]
        ).send()
        
    except Exception as e:
        await cl.Message(content=f"⚠️ Error processing question: {str(e)}").send()

if __name__ == "__main__":
    import asyncio
    asyncio.run(cl.run())  # Ensure async execution
