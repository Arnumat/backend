from ultralytics import YOLOv10
import os

def get_yolo_model():
    HOME = os.getcwd() 
    model = YOLOv10(f'{HOME}/models/yolo/yolov10/X-size/best.pt')
    return model