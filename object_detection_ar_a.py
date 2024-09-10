import os
import shutil
import numpy as np
import pymongo
import sys

from ultralytics import YOLO
from PIL import Image
from datetime import date 

# Get the train_num from the command line argument
if len(sys.argv) != 2:
    print("Error: train_num argument missing.")
    sys.exit(1)

try:
    train_num = int(sys.argv[1])
except ValueError:
    print("Error: train_num must be an integer.")
    sys.exit(1)

today = date.today()
formatted_date = today.strftime("%d-%m-%Y")
formatted_date_filename = today.strftime("%d_%m_%Y") 
train_num = str(train_num)

connection_string = "mongodb+srv://alvinwongster:alvinwongster@testcluster.trqdcfv.mongodb.net/?retryWrites=true&w=majority&appName=testcluster"
try: 
    client = pymongo.MongoClient(connection_string)
except Exception as e:
    print(f"Error: {str(e)}")

database = client["pages"]

# Step 4 - create a collection
myCollection = database["tasks"]

# Load the trained YOLOv8 model
model = YOLO('best.pt')

# Define the source folder and target folder
source_folder = "images"
defects_folder = "defects"

# Define custom confidence thresholds for each label
label_thresholds = {
    'lviv_open': 0.94,
    'rgs_open': 0.55,
    'rgs_screw_missing': 0.43
}

# Check if defects folder exists and clean it
if os.path.exists(defects_folder):
    for filename in os.listdir(defects_folder):
        file_path = os.path.join(defects_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')
else:
    os.makedirs(defects_folder)

# Loop through the images in the source folder
for filename in os.listdir(source_folder):
    if filename.endswith(('.png', '.jpg', '.jpeg')):  
        img_path = os.path.join(source_folder, filename)

        try:
            img = Image.open(img_path)
            img.verify()  
        except (IOError, SyntaxError) as e:
            print(f"Image {filename} is invalid. Error: {e}")
            continue  
        
        # Run YOLO detection
        results = model(img_path)

        valid_detection = False
        detected_label = None
        
        for detection in results[0].boxes:
            label = detection.cls  
            confidence = detection.conf  
            label_name = model.names[int(label)]
            
            if label_name in label_thresholds and confidence >= label_thresholds[label_name]:
                valid_detection = True
                detected_label = label_name
                break 
        
        if valid_detection and detected_label:
            result_img = results[0].plot()  
            result_pil_image = Image.fromarray(np.uint8(result_img[:,:,[2,1,0]]))
            
            filename_without_extension = os.path.splitext(filename)[0]
            new_filename = f"{detected_label}_{filename_without_extension}_{formatted_date_filename}.jpg"
            output_path = os.path.join(defects_folder, new_filename)
            result_pil_image.save(output_path)  

            task_data = {
                "date": formatted_date,  
                "location": "side",
                "sensor": "sony",
                "task_status": False,  
                "image_name": new_filename,
                "train_num": train_num,
                "carriage_num": new_filename,
            }
            try:
                myCollection.insert_one(task_data)
                print(f"Data for {new_filename} saved to MongoDB.")
            except Exception as e:
                print(f"Failed to save data for {new_filename}. Error: {e}")


