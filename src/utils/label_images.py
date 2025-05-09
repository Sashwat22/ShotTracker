import cv2
import os
import numpy as np

def create_label(image_path, label_path):
    """Create a YOLO format label for an image."""
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not read image: {image_path}")
        return
    
    height, width = img.shape[:2]
    
    # Create window and set mouse callback
    window_name = "Label Basketball"
    cv2.namedWindow(window_name)
    
    # Variables to store bounding box coordinates
    start_point = None
    end_point = None
    drawing = False
    label_created = False
    
    def mouse_callback(event, x, y, flags, param):
        nonlocal start_point, end_point, drawing, label_created
        
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            start_point = (x, y)
            label_created = False
            
        elif event == cv2.EVENT_MOUSEMOVE:
            if drawing:
                img_copy = img.copy()
                cv2.rectangle(img_copy, start_point, (x, y), (0, 255, 0), 2)
                cv2.imshow(window_name, img_copy)
                
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            end_point = (x, y)
            
            # Convert to YOLO format (x_center, y_center, width, height)
            x_center = (start_point[0] + end_point[0]) / 2 / width
            y_center = (start_point[1] + end_point[1]) / 2 / height
            box_width = abs(end_point[0] - start_point[0]) / width
            box_height = abs(end_point[1] - start_point[1]) / height
            
            # Save label
            with open(label_path, 'w') as f:
                f.write(f"0 {x_center} {y_center} {box_width} {box_height}\n")
            
            # Draw final rectangle
            cv2.rectangle(img, start_point, end_point, (0, 255, 0), 2)
            cv2.imshow(window_name, img)
            label_created = True
            
            # Print box dimensions
            print(f"\nBox dimensions:")
            print(f"Width: {box_width:.3f} of image width")
            print(f"Height: {box_height:.3f} of image height")
            print(f"Center: ({x_center:.3f}, {y_center:.3f})")
    
    cv2.setMouseCallback(window_name, mouse_callback)
    cv2.imshow(window_name, img)
    
    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):  # Quit
            return False
        elif key == ord('n'):  # Next image
            if label_created:
                return True
            else:
                print("\nPlease draw a bounding box before proceeding!")
        elif key == ord('r'):  # Redo
            if os.path.exists(label_path):
                os.remove(label_path)
            img_copy = img.copy()
            cv2.imshow(window_name, img_copy)
            label_created = False
        elif key == ord('s'):  # Skip
            if os.path.exists(label_path):
                os.remove(label_path)
            return True
    
    cv2.destroyAllWindows()

def label_all_images():
    """Label all images in the training directory."""
    image_dir = "data/train/images"
    label_dir = "data/train/labels"
    
    # Create label directory if it doesn't exist
    os.makedirs(label_dir, exist_ok=True)
    
    # Get all image files
    image_files = [f for f in os.listdir(image_dir) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    print("\n=== Basketball Labeling Tool ===")
    print("Instructions:")
    print("- Click and drag to draw a box around the basketball")
    print("- Press 'r' to redo the current label")
    print("- Press 'n' to move to the next image")
    print("- Press 's' to skip this image (no ball visible)")
    print("- Press 'q' to quit")
    print("\nTips for good labels:")
    print("1. Make sure the box tightly fits the basketball")
    print("2. Include the entire ball in the box")
    print("3. Try to make the box as square as possible")
    print("4. If the ball is partially occluded, estimate its full size")
    print("5. If the ball is not visible, press 's' to skip")
    print("==============================\n")
    
    for i, image_file in enumerate(image_files, 1):
        image_path = os.path.join(image_dir, image_file)
        label_path = os.path.join(label_dir, image_file.rsplit('.', 1)[0] + '.txt')
        
        print(f"\nLabeling image {i}/{len(image_files)}: {image_file}")
        if not create_label(image_path, label_path):
            print("\nLabeling stopped by user.")
            break

if __name__ == "__main__":
    label_all_images() 