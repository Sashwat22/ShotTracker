from ultralytics import YOLO
import os
from datetime import datetime

def train_model():
    """Train YOLOv8 model on basketball dataset."""
    # Create output directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join('runs', 'train', f'basketball_{timestamp}')
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize model
    model = YOLO('yolov8n.pt')  # load a pretrained model (recommended for training)
    
    # Train the model
    results = model.train(
        data='src/config/data.yaml',  # path to data config file
        epochs=100,
        imgsz=640,
        batch=8,  # reduced batch size
        device='mps',  # use MPS acceleration
        workers=4,  # reduced workers
        patience=50,
        save=True,
        save_period=10,
        cache=False,
        exist_ok=False,
        pretrained=True,
        optimizer='auto',
        verbose=True,
        seed=0,
        deterministic=True,
        single_cls=True,
        rect=False,
        cos_lr=False,
        close_mosaic=10,
        max_det=100,  # limit maximum detections
        iou=0.5,  # lower IOU threshold for NMS
        project=output_dir
    )
    
    # Save the trained model
    model.save(os.path.join(output_dir, 'basketball_model.pt'))
    
    print(f"\nTraining completed. Model saved to: {output_dir}")
    print("\nTraining metrics:")
    print(f"mAP50: {results.results_dict['metrics/mAP50(B)']:.3f}")
    print(f"mAP50-95: {results.results_dict['metrics/mAP50-95(B)']:.3f}")
    print(f"Precision: {results.results_dict['metrics/precision(B)']:.3f}")
    print(f"Recall: {results.results_dict['metrics/recall(B)']:.3f}")

if __name__ == "__main__":
    train_model() 