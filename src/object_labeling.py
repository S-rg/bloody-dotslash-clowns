from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import torch
import cv2
import numpy as np

# Load the pre-trained ViT model and processor
model_name = "google/vit-base-patch16-224"
model = ViTForImageClassification.from_pretrained(model_name)
processor = ViTImageProcessor.from_pretrained(model_name)

# Function to label an image
def label_image(image_input):
    # Check if the input is a file path, PIL Image, or OpenCV image
    if isinstance(image_input, str):  # If it's a path
        image = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, Image.Image):  # If it's already a PIL Image
        image = image_input.convert("RGB")
    elif isinstance(image_input, np.ndarray):  # If it's an OpenCV image (NumPy array)
        # Convert the cv2 image to RGB format and then to PIL
        image = Image.fromarray(cv2.cvtColor(image_input, cv2.COLOR_BGR2RGB))
    else:
        raise ValueError("Input must be a file path, PIL.Image.Image, or a NumPy array.")

    
    # Preprocess the image
    inputs = processor(images=image, return_tensors="pt")
    
    # Perform inference
    with torch.no_grad():
        outputs = model(**inputs)
    
    # Get the predicted label
    logits = outputs.logits
    predicted_label = logits.argmax(-1).item()
    label = model.config.id2label[predicted_label]
    return label.split(',')[0]


if __name__ == "__main__":
    image_path = Image.open('/Users/suraj/Downloads/bloody-dotslash-clowns/assets/images_to_label/gold_lid_front.jpeg').convert('RGB')
    label = label_image(image_path)
    print(f"The object in the image is: {label}")
