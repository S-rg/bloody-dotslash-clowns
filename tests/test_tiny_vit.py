from transformers import ViTForImageClassification, ViTImageProcessor
from PIL import Image
import torch

# Load the pre-trained ViT model and processor
model_name = "google/vit-base-patch16-224"
model = ViTForImageClassification.from_pretrained(model_name)
processor = ViTImageProcessor.from_pretrained(model_name)

# Function to label an image
def label_image(image_input):
    # Check if input is a file path or already an Image object
    if isinstance(image_input, str):  # If it's a path
        image = Image.open(image_input).convert("RGB")
    elif isinstance(image_input, Image.Image):  # If it's already a PIL Image
        image = image_input.convert("RGB")
    else:
        raise ValueError("Input must be a file path or a PIL.Image.Image object.")
    
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

# Test the function
image_path = Image.open('/Users/suraj/Downloads/bloody-dotslash-clowns/assets/images_to_label/gold_lid_front.jpeg').convert('RGB')
label = label_image(image_path)
print(f"The object in the image is: {label}")
