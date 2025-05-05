from ultralytics import YOLO

if __name__ == '__main__':
    model = YOLO('yolov8n.pt')
    model.train(
        data='data/basketball.yaml',
        epochs=50,
        imgsz=640,
        batch=16,
        name='bball_run'
    )
