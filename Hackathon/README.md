# SnapSense: Accessible AI-Powered Image Analysis

## Overview
SnapSense is an AI-driven accessibility tool that provides detailed image analysis, caption generation, and voice-based interactions. It utilizes state-of-the-art models for image captioning, vision-language question answering (VQA), and accessibility-focused scene understanding. The system also integrates Bluetooth-based image transfer for seamless mobile-device interaction.

The application utilizes BLIP for captioning, ViLT for Visual Question Answering (VQA), and OpenCV for image processing, reducing latency, dependency on the cloud, and privacy concerns. The models are optimized for deployment on Snapdragon devices, ensuring efficient performance. The user-friendly interface is built using Chainlit to showcase SnapSense's capabilities.

![SnapSense in Action](assets/snapsense_demo.gif)

## Contributors
- **Dhanashri Deshpande** - https://www.linkedin.com/in/ddhanashri/
- **Saumya Mishra** - https://www.linkedin.com/in/saumya-mishra-a85430156/
- **Poorva Barve** - https://www.linkedin.com/in/poorvabarve/
- **Alka Tripathi** - https://www.linkedin.com/in/alka-t/
- **Ronald Rommel Myloth** - https://www.linkedin.com/in/ronald-rommel/
  
## Features
- **Real-Time Image Captioning**: Generates captions using a pre-trained BLIP model.
- **Vision-Language Question Answering (VQA)**: Answers specific questions about an image.
- **Scene Detection**: Classifies image content to improve accessibility.
- **Text-to-Speech (TTS)**: Converts image descriptions to speech using Edge TTS.
- **Bluetooth Image Transfer**: Enables image sharing from mobile devices.
- **Automated Processing Pipeline**: Handles image preprocessing, model inference, and response generation.

## Preview
**SnapSense Live Preview**

## Installation

### Clone the Repository
Clone the project repository to your local machine:
git clone https://github.com/your-repo/snapdragon-ai-captioning.git
cd snapdragon-ai-captioning

### Create and activate virtual environment
python -m venv venv
source venv/bin/activate

### Prerequisites
cd Hackathon
Ensure you have the following dependencies installed:
- Python 3.8+
- PyTorch
- Transformers (Hugging Face)
- OpenCV
- ONNX Runtime
- Edge TTS - 6.1 and above
- Chainlit
- Bluetooth Libraries (Bleak, PyBluez)
- You can install this altogether using pip install -r requirements.txt

### Install Required Packages
```bash
pip install torch torchvision transformers onnxruntime edge-tts gtts bleak pybluez chainlit opencv-python numpy
```

## Run and Usage Instructions

### 1. Running the Bluetooth Server
```bash
cd Hackathon
python src/bluetooth_server.py
```

### 2. Running the Chat-based Interface (SnapSense UI)
```bash
chainlit run src/app.py --port 8001
```

## Architecture
1. **Image Input**: The user uploads an image via Bluetooth or the UI.
2. **Processing Pipeline**:
   - The vision model extracts features.
   - The language model generates captions.
   - The VQA model answers user questions.
   - The accessibility handler creates a detailed description.
   - The text is converted to speech using Edge TTS.
3. **User Interaction**: The system returns:
   - A text-based description.
   - An audio file for accessibility.

## Bluetooth Integration
- The server listens for image transfers via Bluetooth.
- Received images are automatically processed and described.
- The generated response is converted to an audio file.

## Examples
The `examples/` folder includes sample input and output files to demonstrate SnapSense's capabilities:
- `example_image.jpg` – A sample image for caption generation.
- `example_caption.txt` – Shows how the original image is transformed into a caption and text description.
- `example_vqa.txt` – Demonstrates VQA responses to common image-related queries.


## Cloud vs. Local Execution
- **Runs Locally**: BLIP, ViLT, ResNet-50, OpenCV *(after initial download and caching)*
- **Requires Internet**: Edge TTS *(Cloud-based Speech Synthesis)*

## Future Enhancements
- **Complete ONNX Integration** for fully optimized on-device execution.
- **Replace Edge TTS with a Local Speech Engine** to remove cloud dependency.
- **Mobile App Integration**: A dedicated app for a seamless experience.
- **Multilingual Support**: Expanding TTS and text processing to multiple languages.
- **Edge Computing**: Optimized models for deployment on mobile devices.

## Use Cases
### 1. Accessibility for Visually Impaired Users
- Converts images into descriptive text and audio to help visually impaired individuals understand their surroundings.
- **Example:** Real-time AI-powered screen readers that describe objects, people, or scenes.

### 2. Enhanced Social Media & Content Creation
- Generates context-aware captions by analyzing both images and audio.
- **Example:** Auto-captioning for Instagram, TikTok, and YouTube, making content more engaging and accessible.

### 3. Surveillance & Security
- Uses AI-powered captioning to analyze CCTV footage, describe incidents, and provide real-time alerts.
- **Example:** Smart security systems that detect and narrate suspicious activities.

### 4. E-Commerce & Retail
- Provides automated product descriptions by analyzing images and spoken reviews.
- **Example:** AI-driven product tagging on Amazon or fashion websites.

### 5. Education & E-Learning
- Converts visual content and spoken lectures into text captions, making learning materials more accessible.
- **Example:** AI-driven lecture transcription with slide-based captioning.

### 6. Healthcare & Assistive Tech
- Helps doctors analyze medical images (X-rays, MRIs) and generate automated reports.
- **Example:** AI-powered captioning for telemedicine and patient monitoring.

### 7. Smart Virtual Assistants & Chatbots
- Enhances chatbots with image/audio recognition, making interactions more dynamic.
- **Example:** A virtual assistant that can “see” and “hear” the user, responding accordingly.

## License
This project is licensed under the [MIT License](../LICENSE).

