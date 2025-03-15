import torch
import torchvision.models as models

# Load a pre-trained vision model (e.g., ResNet-50)
model = models.resnet50(pretrained=True)
model.eval()

# Export the model to ONNX
dummy_input = torch.randn(1, 3, 256, 256)  # Example input
onnx_path = "models/vision_model.onnx"
torch.onnx.export(
    model,
    dummy_input,
    onnx_path,
    input_names=["input_image"],
    output_names=["features"],
    dynamic_axes={"input_image": {0: "batch_size"}},
    opset_version=12,
)
print(f"Vision model exported to {onnx_path}")