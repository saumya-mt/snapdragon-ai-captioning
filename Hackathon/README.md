# snapdragon-ai-captioning
Snapdragon-Powered AI for Real-Time Image Captioning
Description
This project demonstrates an AI-powered image captioning application that generates captions for uploaded images in real-time. The application uses a combination of vision and language models exported to ONNX format and is optimized for deployment on Snapdragon devices. A user-friendly interface is built using Chainlit to showcase the functionality.

Developers
Name: Saumya Mishra
Contact: LinkedIn | Email

Setup Instructions
1. Clone the Repository
Clone the project repository to your local machine:
git clone https://github.com/your-repo/snapdragon-ai-captioning.git
cd snapdragon-ai-captioning

2. Set Up a Virtual Environment
Create and activate a Python virtual environment:

python3 -m venv .venv
source .venv/bin/activate

3. Install Dependencies
Install the required Python packages:
pip install -r requirements.txt

4. Install PyTorch
Install PyTorch (CPU version for macOS):
pip install torch torchvision torchaudio
For other platforms or CUDA support, refer to the PyTorch installation guide.

5. Install OpenCV
Install OpenCV for image processing:
pip install opencv-python
If you encounter issues with GUI-related functions, use the headless version:
pip install opencv-python-headless

6. Verify Installation
Ensure all dependencies are installed correctly:

Run and Usage Instructions
1. Export Models
Before running the application, ensure the vision and language models are exported to ONNX format. Use the provided scripts:
cd Hackathon
python3 src/export_vision_model.py
python3 src/export_language_model.py

2. Start the Chainlit App
Run the Chainlit app to launch the user interface:
chainlit run src/app.py

3. Access the App
Open your browser and navigate to:
http://localhost:8000

4. Generate Captions
Type upload in the chat to upload an image.
Upload an image from the images/test_images directory or any other image.
The app will generate a caption for the uploaded image and display it.
Project Structure
Hackathon/
├── .venv/                  # Virtual environment
├── caption-env/            # Environment-specific files
├── images/
│   └── test_images/        # Sample images for testing
│       ├── img1.jpeg
│       ├── img2.jpeg
│       ├── img3.jpeg
│       └── img4.jpeg
├── models/                 # ONNX models
│   ├── language_model.onnx
│   └── vision_model.onnx
├── src/                    # Source code
│   ├── export_language_model.py
│   ├── export_vision_model.py
│   └── image_captioning.py
└── tests/                  # Test scripts
Dependencies
The following dependencies are required for the project:

chainlit==0.6.0
onnxruntime==1.15.1
onnx==1.14.0
Pillow==9.5.0
torch==2.0.1
torchvision==0.15.2
torchaudio==2.0.2
numpy==1.24.3
opencv-python==4.5.5.64
To install all dependencies, run:
pip install -r requirements.txt