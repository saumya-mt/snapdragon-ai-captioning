from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load the pre-trained language model
model_name = "distilgpt2"
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Export the model to ONNX
dummy_input = torch.randint(0, tokenizer.vocab_size, (1, 10))  # Example input
onnx_path = "models/language_model.onnx"
torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    input_names=["input_ids"],
    output_names=["logits"],
    dynamic_axes={"input_ids": {0: "batch_size", 1: "sequence_length"}},
    opset_version=14,  # Updated to opset version 14
)
print(f"Language model exported to {onnx_path}")

