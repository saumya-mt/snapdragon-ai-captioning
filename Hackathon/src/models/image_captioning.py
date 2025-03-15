import cv2
import numpy as np
import onnxruntime
from transformers import AutoTokenizer, BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import sys
import os


def preprocess_image(image_path):
    print(f"Attempting to load image from: {image_path}")

    # Check if file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Read and resize the image to 256x256 pixels
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Unable to load image from {image_path}")

    print(f"Original image shape: {image.shape}")
    image = cv2.resize(image, (256, 256))
    print(f"Resized image shape: {image.shape}")

    # Normalize pixel values to [0,1] and convert to float32
    image = image.astype(np.float32) / 255.0

    # Convert from (H, W, C) to (C, H, W)
    image = np.transpose(image, (2, 0, 1))

    # Add batch dimension
    image = np.expand_dims(image, axis=0)
    print(f"Final preprocessed image shape: {image.shape}")
    return image


def run_vision_model(image_np, session):
    print("Running vision model...")
    input_name = session.get_inputs()[0].name
    print(f"Model input name: {input_name}")
    outputs = session.run(None, {input_name: image_np})
    features = outputs[0]
    print(f"Extracted features shape: {features.shape}")
    return features


def generate_caption_with_blip(image_path):
    """
    Generate a caption for the given image using the BLIP model.

    Args:
        image_path (str): Path to the input image.

    Returns:
        str: Generated caption for the image.
    """
    # Load the pre-trained BLIP model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    # Load and preprocess the image
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")

    # Generate the caption
    outputs = model.generate(**inputs)
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    return caption


def main(image_path):
    try:
        print(f"\nStarting image captioning for: {image_path}")

        # Check for models
        vision_model_path = "models/vision_model.onnx"
        language_model_path = "models/language_model.onnx"

        if not os.path.exists(vision_model_path):
            raise FileNotFoundError(f"Vision model not found at: {vision_model_path}")
        if not os.path.exists(language_model_path):
            raise FileNotFoundError(f"Language model not found at: {language_model_path}")

        # Preprocess the input image
        image_np = preprocess_image(image_path)

        # Load and run vision model
        print("\nLoading vision model...")
        vision_session = onnxruntime.InferenceSession(vision_model_path)
        features = run_vision_model(image_np, vision_session)

        # Generate caption using BLIP
        print("\nGenerating caption using BLIP...")
        caption = generate_caption_with_blip(image_path)
        print("\nGenerated Caption:")
        print(caption)

    except Exception as e:
        print(f"\nError occurred: {str(e)}")
        print("\nTraceback:")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python image_captioning.py <image_path>")
        print("Example: python image_captioning.py images/test_images/img1.jpeg")
        sys.exit(1)
    main(sys.argv[1])