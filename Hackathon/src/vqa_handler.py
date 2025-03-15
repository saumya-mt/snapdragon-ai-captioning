from transformers import ViltProcessor, ViltForQuestionAnswering
import torch
from PIL import Image

class VQAHandler:
    def __init__(self):
        # Initialize VQA model
        self.processor = ViltProcessor.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
        self.model = ViltForQuestionAnswering.from_pretrained("dandelin/vilt-b32-finetuned-vqa")
        
    def get_answer(self, image_path: str, question: str) -> dict:
        """
        Get answer for a question about an image
        """
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        
        # Prepare inputs
        inputs = self.processor(image, question, return_tensors="pt")
        
        # Get prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = torch.nn.functional.softmax(logits, dim=-1)
            
            # Get top 3 predictions
            top_probs, top_indices = torch.topk(probs[0], 3)
            
            results = []
            for prob, idx in zip(top_probs, top_indices):
                answer = self.model.config.id2label[idx.item()]
                confidence = prob.item()
                results.append({
                    "answer": answer,
                    "confidence": f"{confidence:.2%}"
                })
                
        return {
            "main_answer": results[0]["answer"],
            "confidence": results[0]["confidence"],
            "alternatives": results[1:]
        } 