# Shootaround Statistic Keeper

A computer vision-based system for tracking basketball shots and generating shooting statistics. This project uses YOLO for object detection and tracking to analyze basketball shots, detect makes/misses, and calculate shooting statistics.

## Project Goals

- Detect and track basketballs in real-time
- Determine shot outcomes (makes vs. misses)
- Calculate shot distances and shooting statistics
- Generate detailed shot analytics

## Project Structure

```
.
├── data/                  # Dataset and configuration files
│   ├── raw/              # Raw video footage
│   ├── processed/        # Processed video frames
│   └── annotations/      # Training annotations
├── models/               # Trained model weights
├── src/                  # Source code
│   ├── detection/        # Ball detection and tracking
│   ├── analysis/         # Shot analysis and statistics
│   ├── calibration/      # Camera calibration
│   └── utils/           # Utility functions
├── train.py             # Training script
├── xml_to_YOLO.py       # Data conversion utility
└── requirements.txt      # Project dependencies
```

## Features

- Real-time basketball detection and tracking
- Shot outcome detection (makes vs. misses)
- Distance measurement and calibration
- Shooting statistics generation
- Trajectory modeling and analysis
- Shot timing and height calculations

## Prerequisites

- Python 3.8 or higher
- CUDA-capable GPU (recommended for training)
- Camera for video capture

## Installation

1. Clone the repository:
```bash
git clone [your-repository-url]
cd 445Proj
```

2. Create a virtual environment:
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

### Running the System

1. Camera Calibration:
```bash
python src/calibration/calibrate.py
```

2. Shot Tracking:
```bash
python src/detection/track.py
```

3. Statistics Generation:
```bash
python src/analysis/stats.py
```

## Project Milestones

1. Basketball Detection and Tracking (Weeks 1-2)
   - Implement YOLO model for ball detection
   - Frame-by-frame ball tracking
   - Trajectory modeling

2. Basketball-Hoop Interaction (Weeks 2-4)
   - Shot outcome detection
   - Multiple camera angle support
   - Make/miss classification

3. Statistics and Distance (Weeks 3-5)
   - Camera calibration
   - Distance measurement
   - Shooting statistics generation

4. Testing and Validation (Weeks 4-5)
   - Manual video labeling
   - System accuracy testing
   - Performance optimization

## Team Members

- Sashwat: Ball tracking implementation and statistic aggregation
- Kaz: Hoop-ball interaction logic for detecting makes vs. misses
- Ritul: Distance measurement setup and calibration

## License

[Add your license information here]

## Contributing

[Add contribution guidelines if applicable]