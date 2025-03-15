#visual_qa.py
import torch
from transformers import BlipProcessor, BlipForQuestionAnswering
from PIL import Image

# Load BLIP-VQA Model
vqa_processor = BlipProcessor.from_pretrained("Salesforce/blip-vqa-base")
vqa_model = BlipForQuestionAnswering.from_pretrained("Salesforce/blip-vqa-base")

# Answer Image-Related Questions
def answer_question(image_path, question):
    image = Image.open(image_path).convert("RGB")

    # Process image + text input
    inputs = vqa_processor(image, question, return_tensors="pt")

    with torch.no_grad():
        out = vqa_model.generate(**inputs)

    answer = vqa_processor.decode(out[0], skip_special_tokens=True)
    return answer
