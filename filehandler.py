import os
import shutil
import random

# Set your paths
img_dir = 'all_images'
train_dir = 'train'
test_dir = 'test'

# Ensure train and test directories exist
os.makedirs(train_dir, exist_ok=True)
os.makedirs(test_dir, exist_ok=True)

# Function to clear a directory
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

# Clear the train and test directories before starting
clear_directory(train_dir)
clear_directory(test_dir)

# Function to copy files to destination
def copy_files(file_list, dest_dir):
    for jpg, txt in file_list:
        shutil.copy(jpg, dest_dir)
        shutil.copy(txt, dest_dir)

# List to store file pairs
file_pairs = []

# Traverse through the files in the current subdirectory
for file in os.listdir(img_dir):
    if file.endswith('.jpg'):
        jpg_file = os.path.join(img_dir, file)
        txt_file = os.path.join(img_dir, file.replace('.jpg', '.txt'))
        if os.path.exists(txt_file):
            file_pairs.append((jpg_file, txt_file))
    
    file_name = "classes.txt"
    current_path = os.path.join(os.getcwd(), file_name)

# Check if the file exists and its name matches
    if os.path.isfile(current_path) and file_name == "classes.txt":
        # Specify the destination path (one folder up)
        destination_path = os.path.join(os.getcwd(), "..", file_name)
        
        # Move the file
        shutil.move(current_path, destination_path)
        print(f"{file_name} has been moved one folder up.")
    else:
        print(f"{file_name} does not exist in the current directory.")

# Shuffle the list to ensure randomness
random.shuffle(file_pairs)

# Split the data (80% train, 20% test)
split_index = int(0.8 * len(file_pairs))
train_files = file_pairs[:split_index]
test_files = file_pairs[split_index:]

# Copy train files
copy_files(train_files, train_dir)

# Copy test files
copy_files(test_files, test_dir)

# Print summary for the current folder
total_items = len(file_pairs)
print(f"Total number of items in {img_dir}: {total_items}")
print(f"{len(train_files)} items copied to train, {len(test_files)} items copied to test\n")