import os
import shutil
import numpy as np

from ultralytics import YOLO
from PIL import Image

# Load the trained YOLOv8 model
model = YOLO('best.pt')

# Define the source folder and target folder
source_folder = "test_images"
output_folder = "labelled_images"

# Check if the output folder exists
if os.path.exists(output_folder):
    # If the folder exists, delete all contents
    for filename in os.listdir(output_folder):
        file_path = os.path.join(output_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove the file
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove the folder
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
else:
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder)

# Loop through the images in the source folder
for filename in os.listdir(source_folder):
    if filename.endswith(('.png', '.jpg', '.jpeg')):  # Ensure it's an image
        img_path = os.path.join(source_folder, filename)

        # Check if the image can be opened
        try:
            img = Image.open(img_path)
            img.verify()  # Verify the image is valid
        except (IOError, SyntaxError) as e:
            print(f"Image {filename} is invalid. Error: {e}")
            continue  # Skip to the next image
        
        # Run YOLO detection
        results = model(img_path)
        
        # Check each detection in the results
        for detection in results[0].boxes:
            label = detection.cls  # Class label index
            confidence = detection.conf  # Confidence score
            
            # Get the label name using the model's class names
            label_name = model.names[int(label)]
            
            # This returns an image array with the boxes drawn
            result_img = results[0].plot()

            # Convert array back to an image (ensure the correct color channel order)
            result_pil_image = Image.fromarray(np.uint8(result_img))

            # Save the image to the output folder with the original filename
            result_pil_image.save(os.path.join(output_folder, filename))

        print(f"Processed and saved {filename} with YOLO detection results.")


