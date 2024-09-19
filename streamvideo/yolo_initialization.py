import os
import torch
from ultralytics import YOLOv10

yolo_model = None

def initialize_yolo_model():
    global yolo_model
    HOME = os.getcwd()
    if yolo_model is None:
        print('loading yolo model ....')
        yolo_model = YOLOv10(f'{HOME}/models/yolo/yolov10/X-size/best.pt')
    if torch.cuda.is_available():
        yolo_model.to('cuda')
    return yolo_model


def get_yolo_model():
    global yolo_model
    if yolo_model is None:
        initialize_yolo_model()
        
    return yolo_model

  