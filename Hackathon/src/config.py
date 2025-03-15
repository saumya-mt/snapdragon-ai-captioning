# VQA model configuration
VQA_CONFIG = {
    "model_name": "dandelin/vilt-b32-finetuned-vqa",
    "max_length": 32,
    "top_k": 3
}

# Suggested questions for different image types
SUGGESTED_QUESTIONS = {
    "general": [
        "What is the main subject in the image?",
        "What colors are present?",
        "Is this indoors or outdoors?",
        "What time of day is it?"
    ],
    "nature": [
        "What kind of landscape is this?",
        "What weather conditions are visible?",
        "Are there any animals in the image?",
    ],
    "urban": [
        "What type of buildings are shown?",
        "Is this a city or suburban area?",
        "Are there any vehicles visible?",
    ]
} 