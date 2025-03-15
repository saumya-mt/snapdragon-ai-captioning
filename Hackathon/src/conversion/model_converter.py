import torch
from transformers import (
    BlipProcessor, 
    BlipForConditionalGeneration,
    ViltProcessor, 
    ViltForQuestionAnswering
)
import logging
from pathlib import Path
import onnx

class ModelConverter:
    def __init__(self):
        self.output_dir = Path("models")
        self.output_dir.mkdir(exist_ok=True)
        
        try:
            # Initialize BLIP model
            self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            self.blip_model.eval()
            logging.info("Successfully loaded BLIP model")

            # Initialize VQA model
            self.vqa_processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
            self.vqa_model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
            self.vqa_model.eval()
            logging.info("Successfully loaded VQA model")
            
        except Exception as e:
            logging.error(f"Failed to load models: {str(e)}")
            raise

    def convert_vision_to_onnx(self):
        """Convert BLIP vision model to ONNX"""
        try:
            vision_path = self.output_dir / "blip_vision.onnx"
            
            # Create dummy input with values between 0 and 1
            dummy_input = torch.rand(1, 3, 224, 224)
            
            # Process through BLIP processor
            inputs = self.blip_processor(
                images=dummy_input,
                return_tensors="pt",
                do_rescale=False
            )
            
            # Create vision model wrapper
            class VisionWrapper(torch.nn.Module):
                def __init__(self, model):
                    super().__init__()
                    self.vision_model = model.vision_model

                def forward(self, pixel_values):
                    return self.vision_model(pixel_values)[0]

            # Create wrapper instance
            vision_wrapper = VisionWrapper(self.blip_model)
            vision_wrapper.eval()
            
            # Export to ONNX
            torch.onnx.export(
                vision_wrapper,
                inputs['pixel_values'],
                vision_path,
                input_names=['pixel_values'],
                output_names=['vision_features'],
                dynamic_axes={
                    'pixel_values': {0: 'batch_size'},
                    'vision_features': {0: 'batch_size'}
                },
                opset_version=11,
                do_constant_folding=True
            )
            
            logging.info(f"Successfully converted vision model to {vision_path}")
            return vision_path
            
        except Exception as e:
            logging.error(f"Failed to convert vision model: {str(e)}")
            raise

    def convert_language_to_onnx(self):
        """Convert BLIP language model to ONNX"""
        try:
            language_path = self.output_dir / "language_model.onnx"
            
            # Create dummy text input
            dummy_text = ["a photo of"]
            inputs = self.blip_processor(
                text=dummy_text,
                return_tensors="pt",
                padding=True
            )
            
            # Create language model wrapper
            class LanguageWrapper(torch.nn.Module):
                def __init__(self, model):
                    super().__init__()
                    self.text_decoder = model.text_decoder

                def forward(self, input_ids, attention_mask):
                    return self.text_decoder(
                        input_ids=input_ids,
                        attention_mask=attention_mask
                    )[0]

            # Create wrapper instance
            language_wrapper = LanguageWrapper(self.blip_model)
            language_wrapper.eval()
            
            # Export to ONNX
            torch.onnx.export(
                language_wrapper,
                (inputs['input_ids'], inputs['attention_mask']),
                language_path,
                input_names=['input_ids', 'attention_mask'],
                output_names=['text_features'],
                dynamic_axes={
                    'input_ids': {0: 'batch_size', 1: 'sequence'},
                    'attention_mask': {0: 'batch_size', 1: 'sequence'},
                    'text_features': {0: 'batch_size', 1: 'sequence'}
                },
                opset_version=11,
                do_constant_folding=True
            )
            
            logging.info(f"Successfully converted language model to {language_path}")
            return language_path
            
        except Exception as e:
            logging.error(f"Failed to convert language model: {str(e)}")
            raise

    def convert_vqa_to_onnx(self):
        """Convert VQA model to ONNX"""
        try:
            vqa_path = self.output_dir / "vqa_model.onnx"
            
            # Create dummy inputs with fixed sizes
            batch_size = 1
            image_size = 384
            seq_length = 40  # Match the actual sequence length from the processor

            dummy_image = torch.rand(batch_size, 3, image_size, image_size)
            dummy_question = "What is in the image?"
            
            # Process inputs
            inputs = self.vqa_processor(
                images=dummy_image,
                text=dummy_question,
                return_tensors="pt",
                padding='max_length',
                max_length=seq_length,
                truncation=True
            )

            # Create VQA model wrapper
            class VQAWrapper(torch.nn.Module):
                def __init__(self, model):
                    super().__init__()
                    self.vilt = model.vilt
                    self.classifier = model.classifier
                    self.image_size = 384
                    self.patch_size = 32
                    self.num_patches = (self.image_size // self.patch_size) ** 2

                def forward(self, pixel_values, input_ids, attention_mask):
                    # Pre-compute image patches
                    batch_size = pixel_values.shape[0]
                    image_embeddings = self.vilt.embeddings.patch_embeddings(pixel_values)
                    image_embeddings = image_embeddings.flatten(2).transpose(1, 2)
                    
                    # Get text embeddings with fixed sequence length
                    text_embeddings = self.vilt.embeddings.text_embeddings(
                        input_ids=input_ids
                    )
                    
                    # Combine embeddings
                    embeddings = torch.cat([image_embeddings, text_embeddings], dim=1)
                    
                    # Create extended attention mask
                    extended_attention_mask = torch.cat([
                        torch.ones(batch_size, self.num_patches, device=attention_mask.device),
                        attention_mask
                    ], dim=1)
                    
                    # Forward through transformer and classifier
                    outputs = self.vilt.encoder(
                        embeddings,
                        attention_mask=extended_attention_mask,
                        return_dict=True
                    )
                    logits = self.classifier(outputs.last_hidden_state[:, 0, :])
                    return logits

            # Create wrapper instance
            vqa_wrapper = VQAWrapper(self.vqa_model)
            vqa_wrapper.eval()

            # Verify input shapes before export
            logging.info(f"Input shapes before export:")
            logging.info(f"pixel_values: {inputs['pixel_values'].shape}")
            logging.info(f"input_ids: {inputs['input_ids'].shape}")
            logging.info(f"attention_mask: {inputs['attention_mask'].shape}")
            
            # Export to ONNX
            torch.onnx.export(
                vqa_wrapper,
                (
                    inputs['pixel_values'],
                    inputs['input_ids'],
                    inputs['attention_mask']
                ),
                vqa_path,
                input_names=['pixel_values', 'input_ids', 'attention_mask'],
                output_names=['logits'],
                dynamic_axes={
                    'pixel_values': {0: 'batch_size'},
                    'input_ids': {0: 'batch_size'},
                    'attention_mask': {0: 'batch_size'}
                },
                opset_version=11,
                do_constant_folding=True
            )
            
            logging.info(f"Successfully converted VQA model to {vqa_path}")
            return vqa_path
            
        except Exception as e:
            logging.error(f"Failed to convert VQA model: {str(e)}")
            raise

    def verify_model(self, model_path):
        """Verify that an ONNX model is valid"""
        try:
            model = onnx.load(model_path)
            onnx.checker.check_model(model)
            logging.info(f"Successfully verified model: {model_path}")
            return True
        except Exception as e:
            logging.error(f"Model verification failed: {str(e)}")
            return False