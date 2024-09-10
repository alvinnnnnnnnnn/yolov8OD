import os
import shutil
import random

# Set your paths
img_dir = 'all_images'
train_img_dir = os.path.join('train', 'images')
train_label_dir = os.path.join('train', 'labels')
test_img_dir = os.path.join('test', 'images')
test_label_dir = os.path.join('test', 'labels')

# Ensure train and test directories and subdirectories exist
os.makedirs(train_img_dir, exist_ok=True)
os.makedirs(train_label_dir, exist_ok=True)
os.makedirs(test_img_dir, exist_ok=True)
os.makedirs(test_label_dir, exist_ok=True)

# Function to clear a directory
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

# Clear the train and test directories before starting
clear_directory(train_img_dir)
clear_directory(train_label_dir)
clear_directory(test_img_dir)
clear_directory(test_label_dir)

# Move classes.txt one directory up
classes_file = os.path.join(img_dir, 'classes.txt')
if os.path.exists(classes_file):
    destination_path = os.path.join(os.getcwd(), '..', 'classes.txt')
    shutil.move(classes_file, destination_path)
    print(f"Moved classes.txt to {destination_path}")
else:
    print("classes.txt does not exist in the 'all_images' folder.")

# Function to copy files to destination (images and labels)
def copy_files(file_list, img_dest_dir, label_dest_dir):
    for jpg, txt in file_list:
        shutil.copy(jpg, img_dest_dir)
        shutil.copy(txt, label_dest_dir)

# List to store file pairs
file_pairs = []

# Traverse through the files in the img_dir
for file in os.listdir(img_dir):
    if file.endswith('.jpg'):
        jpg_file = os.path.join(img_dir, file)
        txt_file = os.path.join(img_dir, file.replace('.jpg', '.txt'))
        if os.path.exists(txt_file):
            file_pairs.append((jpg_file, txt_file))

# Shuffle the list to ensure randomness
random.shuffle(file_pairs)

# Split the data (80% train, 20% test)
split_index = int(0.8 * len(file_pairs))
train_files = file_pairs[:split_index]
test_files = file_pairs[split_index:]

# Copy train files
copy_files(train_files, train_img_dir, train_label_dir)

# Copy test files
copy_files(test_files, test_img_dir, test_label_dir)

# Print summary
total_items = len(file_pairs)
print(f"Total number of items in {img_dir}: {total_items}")
print(f"{len(train_files)} items copied to train (images and labels), {len(test_files)} items copied to test (images and labels)")
