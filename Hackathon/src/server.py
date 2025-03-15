# server.py
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
from Hackathon.src.models.optimized_models import OptimizedModelHandler
from Hackathon.handlers.accessibility_handler import AccessibilityHandler

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize handlers globally
model_handler = OptimizedModelHandler()
accessibility_handler = AccessibilityHandler()
vqa_handler = VQAHandler()

def generate_audio(text, lang='en'):
    """Generate audio from text using gTTS"""
    tts = gTTS(text=text, lang=lang)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
        tts.save(fp.name)
        return fp.name

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Save uploaded image
        image_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(image_path)

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
        audio_path = generate_audio(detailed_description)

        return send_file(audio_path, mimetype='audio/mpeg')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/ask_question', methods=['POST'])
def ask_question():
    data = request.json
    image_path = data.get('image_path')
    question = data.get('question')

    try:
        result = model_handler.answer_question(image_path, question)
        response = f"You asked: {question}. The answer is: {result['answer']}"

        # Convert answer to speech
        audio_path = generate_audio(response)

        return send_file(audio_path, mimetype='audio/mpeg')

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)