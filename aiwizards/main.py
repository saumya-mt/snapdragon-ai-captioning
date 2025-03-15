#main.py
from models.image_captioning import generate_caption
from models.visual_qa import answer_question
from models.text_to_speech import text_to_speech
import os
from tkinter import Tk, filedialog

def select_image():
    Tk().withdraw()  # Hide the root window
    image_path = filedialog.askopenfilename(title="Select an Image", filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    return image_path

def main():
    print("Select an image for captioning...")
    image_path = select_image()

    if not image_path:
        print("No image selected. Exiting.")
        return

    print("Generating caption...")
    caption = generate_caption(image_path)
    print("Caption:", caption)

    print("Converting caption to speech...")
    text_to_speech(caption)

    question = input("Ask a question about the image: ")
    answer = answer_question(image_path, question)
    print(f"Q: {question}\nA: {answer}")

if __name__ == "__main__":
    main()
