import os
import shutil
import random

def create_validation_split(train_dir="data/train", val_dir="data/val", val_ratio=0.2):
    """Split the dataset into training and validation sets."""
    # Create validation directories
    os.makedirs(os.path.join(val_dir, "images"), exist_ok=True)
    os.makedirs(os.path.join(val_dir, "labels"), exist_ok=True)
    
    # Get all image files
    image_files = [f for f in os.listdir(os.path.join(train_dir, "images")) 
                  if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    # Calculate number of validation images
    n_val = int(len(image_files) * val_ratio)
    
    # Randomly select validation images
    val_files = random.sample(image_files, n_val)
    
    # Move files to validation set
    for file in val_files:
        # Move image
        src_img = os.path.join(train_dir, "images", file)
        dst_img = os.path.join(val_dir, "images", file)
        shutil.move(src_img, dst_img)
        
        # Move corresponding label
        label_file = file.rsplit('.', 1)[0] + '.txt'
        src_label = os.path.join(train_dir, "labels", label_file)
        dst_label = os.path.join(val_dir, "labels", label_file)
        if os.path.exists(src_label):
            shutil.move(src_label, dst_label)
    
    print(f"Created validation split:")
    print(f"Training images: {len(image_files) - n_val}")
    print(f"Validation images: {n_val}")

if __name__ == "__main__":
    create_validation_split() 