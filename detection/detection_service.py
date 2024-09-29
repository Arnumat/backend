import os
import cv2
import base64

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
import numpy as np
import pytz

from .yolo_initialization import get_yolo_model

import supervision as sv

from django.utils import timezone

import requests

import time

def run_detection():
    
    # Initialize YOLO model
    model = get_yolo_model()
    
    # static instance
    duration_in_minutes = 10
    duration_in_seconds = duration_in_minutes * 60

    tracker = sv.ByteTrack()
    
    trace_annotator = sv.TraceAnnotator()
    bounding_box_annotator = sv.BoundingBoxAnnotator()
    label_annotator = sv.LabelAnnotator()
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    
    # Capture video from the source (camera or stream)
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Change this to your specific video source

    # Access channel layer to send frames
    channel_layer = get_channel_layer()

    while True:
        ret, frame = cap.read()        
        if not ret:
            break
        
        # Perform detection on the frame using the YOLO model
        results = model(frame)[0]

        detections = sv.Detections.from_ultralytics(results)
        detections = tracker.update_with_detections(detections)
        
        if detections.tracker_id.size > 0:  # Check if there are any detections
            labels = [f"{detections.data['class_name']} #{tracker_id}" for tracker_id in detections.tracker_id]

            annotated_frame = label_annotator.annotate(scene=frame.copy(), detections=detections, labels=labels)
            annotated_frame = bounding_box_annotator.annotate(scene=annotated_frame, detections=detections)
            annotated_frame = trace_annotator.annotate(scene=annotated_frame, detections=detections)

            # Package data detection
            timedetected = timezone.now()
            local_time = timedetected.astimezone(bangkok_tz)
            formatted_datetime = local_time.strftime('%d %B %Y at time %H:%M:%S')  

            # Encode frame as base64 to send over WebSocket
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            base64_frame = base64.b64encode(buffer).decode('utf-8')
            
            # Check detected before saving data  
            detected = len(detections.class_id)
            if detected > 0:
                detectionWrite(base64_frame, detections, timedetected)
                send_line_notify(base64_frame, detected, timedetected)

            async_to_sync(channel_layer.group_send)(
                "video_stream",
                {
                    "type": "video_frame",
                    "frame": base64_frame,
                    "found": detected,
                    "time_detected": formatted_datetime,
                }
            )
        else:
            print("No detections found.")
            _, buffer = cv2.imencode('.jpg',frame)
            base64_frame = base64.b64encode(buffer).decode('utf-8')
            timedetected = timezone.now()
            local_time = timedetected.astimezone(bangkok_tz)
            formatted_datetime = local_time.strftime('%d %B %Y at time %H:%M:%S')  

            async_to_sync(channel_layer.group_send)(
            "video_stream",
                {
                    "type": "video_frame",
                    "frame": base64_frame,
                    "found": 0,
                    "time_detected": formatted_datetime,
                })
    # Release the video capture when done
    cap.release()




def detectionWrite(base64_frame , detections ,time_detect):
    image_path = save_frame_image(base64_frame)
    from .models import LandsnailDetection ,FrameDetection , Species
    frame_instance = FrameDetection(image = image_path, snail_detected = len(detections.class_id), time_detect = time_detect)
    frame_instance.save()
    
    
    for i in range(len(detections.xyxy)):
            # x_min, y_min, x_max, y_max = detections.xyxy[i]
            # detected_coordinate = f"{x_min},{y_min},{x_max},{y_max}"
            class_name = detections.data['class_name'][i]
            conf_score = detections.confidence[i]
            # Get or create Species object
            species = Species.objects.get_or_create(name=class_name)[0]
            
            # Create LandSnailDetectedList instance
            detected_instance = LandsnailDetection(
                conf_score=conf_score,
                frame=frame_instance,
                species=species
            )
            detected_instance.save()
            return
            
def save_frame_image(base64_frame):
    
    
    timestamp = time.time()
    filename = f'frame_{timestamp}.jpg'

    # Construct the full path to the media directory
    media_directory = settings.MEDIA_ROOT  # Assuming MEDIA_ROOT is set in settings.py
    frame_image_path = os.path.join(media_directory, 'frames_detected', filename)

    # Create directory if it does not exist
    os.makedirs(os.path.dirname(frame_image_path), exist_ok=True)
    
    
    # Generate unique filename using timestamp
    image_data = base64.b64decode(base64_frame)

    # Convert byte data to a numpy array
    nparr = np.frombuffer(image_data, np.uint8)

    # Decode the image from the numpy array
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Save the frame image to the specified file path
    cv2.imwrite(frame_image_path, img)

    return frame_image_path


def send_line_notify(frame_byte, detect_count, time_detect):

    line_notify_api = 'https://notify-api.line.me/api/notify'
    token  = "OfHR5ocCfD7v7i6EyHJ4t8FAt0hFj3JcWUg21mmH2AB"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    # Create a message with detection count and time detected
    message = f'Detections: {detect_count}, Time Detected: {time_detect}'
    
    # Prepare the payload
    payload = {
        'message': message
    }
    
    # Send the POST request with an image
    files = {'imageFile': ('detection.jpg', frame_byte, 'image/jpeg')}
    
    requests.post(line_notify_api, headers=headers, data=payload, files=files)
    # response =
    # response = requests.post(line_notify_api, headers=headers, data=payload)    
    return
    # return response
