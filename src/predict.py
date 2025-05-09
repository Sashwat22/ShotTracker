from ultralytics import YOLO
import cv2
import os
from datetime import datetime

def predict_images():
    """Test the trained model on sample images."""
    # Load the trained model
    model = YOLO('runs/train/basketball_20250509_105945/train/weights/best.pt')
    
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join('runs', 'predict', f'basketball_{timestamp}')
    os.makedirs(output_dir, exist_ok=True)
    
    # Test on validation images
    val_dir = 'data/val/images'
    for img_name in os.listdir(val_dir):
        if img_name.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(val_dir, img_name)
            
            # Run prediction
            results = model.predict(
                source=img_path,
                conf=0.25,  # confidence threshold
                save=True,
                save_txt=True,
                save_conf=True,
                project=output_dir,
                name=img_name.rsplit('.', 1)[0]
            )
            
            # Print results
            print(f"\nResults for {img_name}:")
            for r in results:
                boxes = r.boxes
                if len(boxes) > 0:
                    for box in boxes:
                        conf = box.conf[0].item()
                        print(f"Basketball detected with confidence: {conf:.2f}")
                else:
                    print("No basketball detected")

if __name__ == "__main__":
    predict_images() 