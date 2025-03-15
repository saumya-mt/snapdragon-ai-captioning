from transformers import BlipProcessor, ViltProcessor, BlipForConditionalGeneration, ViltForQuestionAnswering
import torch
from PIL import Image
import os

class OptimizedModelHandler:
    def __init__(self):
        # Initialize BLIP for image captioning
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        
        # Initialize ViLT for VQA
        self.vilt_processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
        self.vilt_model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")

    def generate_caption(self, image_path):
        """Generate caption for the image"""
        try:
            # Read and process image
            image = Image.open(image_path).convert('RGB')
            inputs = self.blip_processor(image, return_tensors="pt")
            
            # Generate caption
            outputs = self.blip_model.generate(**inputs)
            caption = self.blip_processor.decode(outputs[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            raise Exception(f"Error generating caption: {str(e)}")

    def answer_question(self, image_path, question):
        """Answer a question about the image"""
        try:
            # Read and process image
            image = Image.open(image_path).convert('RGB')
            inputs = self.vilt_processor(image, question, return_tensors="pt")
            
            # Get answer
            outputs = self.vilt_model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get top answer and confidence
            max_idx = logits.argmax(-1).item()
            answer = self.vilt_model.config.id2label[max_idx]
            confidence = probs[0][max_idx].item()
            
            return {
                "answer": answer,
                "confidence": f"{confidence:.2%}"
            }
            
        except Exception as e:
            raise Exception(f"Error processing question: {str(e)}") 