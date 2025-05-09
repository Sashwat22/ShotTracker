import os
import shutil
import random
from pathlib import Path

def create_dataset_structure():
    """Create the necessary directory structure for YOLO training."""
    # Create train and val directories
    for split in ['train', 'val']:
        for subdir in ['images', 'labels']:
            os.makedirs(f'data/{split}/{subdir}', exist_ok=True)

def split_dataset(train_ratio=0.8):
    """Split the dataset into training and validation sets."""
    # Get all image files
    image_files = [f for f in os.listdir('data/train/images') if f.endswith(('.jpg', '.jpeg', '.png'))]
    random.shuffle(image_files)
    
    # Calculate split point
    split_idx = int(len(image_files) * train_ratio)
    train_files = image_files[:split_idx]
    val_files = image_files[split_idx:]
    
    # Process training files
    for file in train_files:
        # Copy image to train directory
        src_img = os.path.join('data/train/images', file)
        dst_img = os.path.join('data/train/images', file)
        if src_img != dst_img:  # Only copy if source and destination are different
            shutil.copy2(src_img, dst_img)
        
        # Copy corresponding label if it exists
        label_file = file.rsplit('.', 1)[0] + '.txt'
        src_label = os.path.join('data/train/labels', label_file)
        dst_label = os.path.join('data/train/labels', label_file)
        if os.path.exists(src_label) and src_label != dst_label:
            shutil.copy2(src_label, dst_label)
    
    # Process validation files
    for file in val_files:
        # Copy image to val directory
        src_img = os.path.join('data/train/images', file)
        dst_img = os.path.join('data/val/images', file)
        shutil.copy2(src_img, dst_img)
        
        # Copy corresponding label if it exists
        label_file = file.rsplit('.', 1)[0] + '.txt'
        src_label = os.path.join('data/train/labels', label_file)
        dst_label = os.path.join('data/val/labels', label_file)
        if os.path.exists(src_label):
            shutil.copy2(src_label, dst_label)

def create_dataset_yaml():
    """Create the dataset.yaml file for YOLO training."""
    yaml_content = f"""# Dataset configuration
path: {os.path.abspath('data')}  # dataset root dir
train: train/images  # train images (relative to 'path')
val: val/images  # val images (relative to 'path')

# Classes
names:
  0: basketball  # class names
"""
    
    with open('data/dataset.yaml', 'w') as f:
        f.write(yaml_content)

if __name__ == '__main__':
    create_dataset_structure()
    split_dataset()
    create_dataset_yaml()
    print("Dataset preparation complete!") 