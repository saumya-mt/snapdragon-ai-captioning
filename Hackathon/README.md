# SnapSense: Accessible AI-Powered Image Analysis

## Overview
SnapSense is an AI-driven accessibility tool that provides detailed image analysis, caption generation, and voice-based interactions. It utilizes state-of-the-art models for image captioning, vision-language question answering (VQA), and accessibility-focused scene understanding. The system also integrates Bluetooth-based image transfer for seamless mobile-device interaction.

The application utilizes BLIP for captioning, ViLT for Visual Question Answering (VQA), and OpenCV for image processing, reducing latency, dependency on the cloud, and privacy concerns. The models are optimized for deployment on Snapdragon devices, ensuring efficient performance. The user-friendly interface is built using Chainlit to showcase SnapSense's capabilities.

## Features
- **Real-Time Image Captioning**: Generates captions using a pre-trained BLIP model.
- **Vision-Language Question Answering (VQA)**: Answers specific questions about an image.
- **Scene Detection**: Classifies image content to improve accessibility.
- **Text-to-Speech (TTS)**: Converts image descriptions to speech using Edge TTS.
- **Bluetooth Image Transfer**: Enables image sharing from mobile devices.
- **Automated Processing Pipeline**: Handles image preprocessing, model inference, and response generation.

## Installation
### Prerequisites
Ensure you have the following dependencies installed:
- Python 3.8+
- PyTorch
- Transformers (Hugging Face)
- OpenCV
- ONNX Runtime
- Edge TTS
- gTTS (Google Text-to-Speech)
- Bluetooth Libraries (Bleak, PyBluez)

### Install Required Packages
```bash
pip install torch torchvision transformers onnxruntime edge-tts gtts bleak pybluez chainlit opencv-python numpy
```

## Usage

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

## Cloud vs. Local Execution
- **Runs Locally**: BLIP, ViLT, ResNet-50, OpenCV *(after initial download and caching)*
- **Requires Internet**: Edge TTS *(Cloud-based Speech Synthesis)*

## Future Enhancements
- **Complete ONNX Integration** for fully optimized on-device execution.
- **Replace Edge TTS with a Local Speech Engine** to remove cloud dependency.
- **Mobile App Integration**: A dedicated app for a seamless experience.
- **Multilingual Support**: Expanding TTS and text processing to multiple languages.
- **Edge Computing**: Optimized models for deployment on mobile devices.

## Contributors
- **Dhanashri Deshpande** - MS in Computer Science
- **Saumya Mishra** - MS in Computer Science
- **Poorva Barve** - MS in Computer Science (Align)
- **Alka Tripathi** - MS in Computer Science
- **Ronald Rommel Myloth** - MS in Computer Science
- **[Contributor Name](https://github.com/username)**

## License
This project is licensed under the [MIT License](../LICENSE).

