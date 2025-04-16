from ultralytics import YOLO



model = YOLO('yolov8n.pt')
model.train(data = '/ultralytics/cfg/datasets/car_light_dataset.yaml', epochs=20)