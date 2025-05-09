# Basketball Object Detection Project

This project implements a basketball object detection system using YOLOv8 and Deep SORT for real-time tracking. The system is designed to detect and track basketballs in video footage.

## Project Structure

```
.
├── data/               # Dataset and configuration files
├── models/            # Trained model weights
├── src/              # Source code
├── train.py          # Training script
├── xml_to_YOLO.py    # Data conversion utility
└── requirements.txt   # Project dependencies
```

## Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (recommended for training)

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd 445Proj
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Training the Model

To train the model on your dataset:

```bash
python train.py
```

The training script uses the following default parameters:
- Model: YOLOv8n
- Epochs: 50
- Image size: 640x640
- Batch size: 16
- Output directory: 'bball_run'

### Data Conversion

If you have XML annotations that need to be converted to YOLO format:

```bash
python xml_to_YOLO.py
```

## Dependencies

- ultralytics: YOLOv8 implementation
- opencv-python: Computer vision operations
- deep-sort-realtime: Object tracking
- numpy: Numerical operations
- scipy: Scientific computing
- PyQt6: GUI framework

## License

[Add your license information here]

## Contributing

[Add contribution guidelines if applicable]