import os
import shutil
import numpy as np
import pymongo

from ultralytics import YOLO
from PIL import Image
from datetime import date 

today = date.today()
formatted_date = today.strftime("%d-%m-%Y")
formatted_date_filename = today.strftime("%d_%m_%Y") 

connection_string = "mongodb+srv://alvinwongster:alvinwongster@testcluster.trqdcfv.mongodb.net/?retryWrites=true&w=majority&appName=testcluster"
try: 
    client = pymongo.MongoClient(connection_string)
except Exception as e:
    print(f"Error: {str(e)}")

database = client["pages"]

#step 4 - create a collection
myCollection = database["tasks"]

# Load the trained YOLOv8 model
model = YOLO('best.pt')

# Define the source folder and target folder
source_folder = "images"
defects_folder = "defects"

# Define custom confidence thresholds for each label (you can add more labels as needed)
label_thresholds = {
    'lviv_open': 0.94,  # Threshold for 'label_1'
    'rgs_open': 0.55,  # Threshold for 'label_2'
    'rgs_screw_missing': 0.43   # Threshold for 'label_3'
}

# Check if defects folder exists
if os.path.exists(defects_folder):
    # If the folder exists, delete all contents
    for filename in os.listdir(defects_folder):
        file_path = os.path.join(defects_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)  # Remove the file
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)  # Remove the folder
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
else:
    # Create the defects folder if it doesn't exist
    os.makedirs(defects_folder)

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

        # Flag to determine if the image has a valid detection based on the thresholds
        valid_detection = False
        detected_label = None
        
        # Check each detection in the results
        for detection in results[0].boxes:
            label = detection.cls  # Class label index
            confidence = detection.conf  # Confidence score
            
            # Get the label name using the model's class names
            label_name = model.names[int(label)]
            
            # Check if the label is in the threshold dictionary and meets the threshold
            if label_name in label_thresholds and confidence >= label_thresholds[label_name]:
                valid_detection = True
                detected_label = label_name
                break  # No need to check further if one valid detection is found
        
        # If a valid detection is found, copy the image to the defects folder
        if valid_detection and detected_label:
            result_img = results[0].plot()  # This returns an image array with the boxes drawn
            result_pil_image = Image.fromarray(np.uint8(result_img[:,:,[2,1,0]]))
            
            # Extract the filename without extension to ensure correct format
            filename_without_extension = os.path.splitext(filename)[0]
            new_filename = f"{detected_label}_{filename_without_extension}_{formatted_date_filename}.jpg"
            output_path = os.path.join(defects_folder, new_filename)
            result_pil_image.save(output_path)  # Save the plotted image

            task_data = {
                "date": formatted_date,  # Date with dashes for the database
                "location": "side",
                "sensor": "sony",
                "task_status": False,  # Default status is incomplete
                "image_name": new_filename,
            }
            try:
                myCollection.insert_one(task_data)
                print(f"Data for {new_filename} saved to MongoDB.")
            except Exception as e:
                print(f"Failed to save data for {new_filename}. Error: {e}")

