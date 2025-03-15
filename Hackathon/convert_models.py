import logging
from src.conversion.model_converter import ModelConverter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    try:
        # Initialize converter
        converter = ModelConverter()
        
        # Convert and verify BLIP vision model
        logging.info("Converting BLIP vision model...")
        vision_path = converter.convert_vision_to_onnx()
        if converter.verify_model(vision_path):
            logging.info(f"✅ Vision model converted and verified: {vision_path}")
        
        # Convert and verify language model
        logging.info("\nConverting language model...")
        language_path = converter.convert_language_to_onnx()
        if converter.verify_model(language_path):
            logging.info(f"✅ Language model converted and verified: {language_path}")
        
        # Convert and verify VQA model
        logging.info("\nConverting VQA model...")
        vqa_path = converter.convert_vqa_to_onnx()
        if converter.verify_model(vqa_path):
            logging.info(f"✅ VQA model converted and verified: {vqa_path}")
        
    except Exception as e:
        logging.error(f"Conversion failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()