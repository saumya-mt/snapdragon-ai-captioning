#app.py

import sys
import os
import asyncio

# Add the root project directory to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sys
import os
import asyncio
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models.image_captioning import generate_caption
from models.visual_qa import answer_question
from models.text_to_speech import text_to_speech

app = Flask(__name__, static_folder="generated_audio")
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins

# Use absolute path to generated_audio folder
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Backend folder
AUDIO_FOLDER = os.path.abspath(os.path.join(BASE_DIR, "..", "generated_audio"))  # Root folder

UPLOAD_FOLDER = "uploaded_images"
# AUDIO_FOLDER = "generated_audio"  # Folder for generated speech
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# Serve Audio Files Correctly
@app.route("/generated_audio/<filename>")
def serve_audio(filename):
    file_path = os.path.join(AUDIO_FOLDER, filename)
    
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")  # Debugging statement
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(AUDIO_FOLDER, filename, as_attachment=True)

@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["image"]
    image_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(image_path)

    caption = generate_caption(image_path)

    # Fix: Remove file extension before adding .mp3
    base_filename = os.path.splitext(file.filename)[0]  # Removes .jpg/.png
    caption_audio_filename = f"caption_{base_filename}.mp3"
    caption_audio_path = os.path.join(AUDIO_FOLDER, caption_audio_filename)
    
    asyncio.run(text_to_speech(caption, caption_audio_path))

    return jsonify({
        "caption": caption,
        "image_path": image_path,
        "caption_audio_url": f"/generated_audio/{caption_audio_filename}"  #  Correct URL
    })

@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.json
    image_path = data.get("image_path")
    question = data.get("question")

    if not image_path or not question:
        return jsonify({"error": "Missing image or question"}), 400

    answer = answer_question(image_path, question)

    # Fix: Remove file extension before adding .mp3
    base_filename = os.path.splitext(os.path.basename(image_path))[0]  # Removes .jpg/.png
    qa_audio_filename = f"qa_{base_filename}.mp3"
    qa_audio_path = os.path.join(AUDIO_FOLDER, qa_audio_filename)
    
    asyncio.run(text_to_speech(f"Question: {question}. Answer: {answer}", qa_audio_path))

    return jsonify({
        "question": question,
        "answer": answer,
        "qa_audio_url": f"/generated_audio/{qa_audio_filename}"  #  Correct URL
    })

if __name__ == "__main__":
    app.run(debug=True)