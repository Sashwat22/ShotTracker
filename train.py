from ultralytics import YOLO
import torch

def train_model():
    """Train the YOLOv8 model on the basketball dataset."""
    # Check for MPS availability
    if torch.backends.mps.is_available():
        device = "mps"
        print("Using MPS (Metal Performance Shaders) for GPU acceleration")
    else:
        device = "cpu"
        print("MPS device not found, using CPU")
    
    # Load a model
    model = YOLO('yolov8n.pt')  # load a pretrained model (recommended for training)
    
    # Train the model
    results = model.train(
        data='data/dataset.yaml',
        epochs=100,
        imgsz=640,
        batch=16,
        name='basketball_detector',
        device=device  # Use MPS if available
    )
    
    # Validate the model
    results = model.val()
    
    # Export the model
    model.export(format='onnx')  # export the model to ONNX format

if __name__ == '__main__':
    train_model()
