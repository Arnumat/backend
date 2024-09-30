import os
from queue import Full
import cv2
import base64
import time
import numpy as np
import requests
import pytz

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from django.utils import timezone

from .yolo_initialization import get_yolo_model
import supervision as sv

import signal
import threading
import time

shutdown_flag = False

def signal_handler(sig, frame):
    global shutdown_flag
    print("Shutdown signal received.")
    shutdown_flag = True


def run_detection():
    global shutdown_flag
    # Initialize YOLO model
    model = get_yolo_model()

    # Initialize tracker and annotators
    tracker = sv.ByteTrack()
    trace_annotator = sv.TraceAnnotator()
    bounding_box_annotator = sv.BoundingBoxAnnotator()
    label_annotator = sv.LabelAnnotator()


    # Capture video from the source (camera or stream)
    cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    # cap = cv2.VideoCapture(0)
    
    # Change this to your specific video source
    
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return  # Exit if video source is not opened

    print("Video source opened successfully.")

    # Access channel layer to send frames
    channel_layer = get_channel_layer()

    frame_rate = 1
    last_saved_time = time.time()
    
    while not shutdown_flag:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame from video source.")
            break

        # Perform detection on the frame using the YOLO model
        results = model(frame, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)
        detections = tracker.update_with_detections(detections)

        current_time = time.time()

        # Prepare to send frames
        if detections.tracker_id.size > 0:
            labels = [f"{detections.data['class_name']} #{tracker_id}" for tracker_id in detections.tracker_id]
            annotated_frame = label_annotator.annotate(scene=frame.copy(), detections=detections, labels=labels)
            annotated_frame = bounding_box_annotator.annotate(scene=annotated_frame, detections=detections)
            annotated_frame = trace_annotator.annotate(scene=annotated_frame, detections=detections)
            # Encode the annotated frame as base64 for WebSocket transmission
            base64_frame = encode_frame_as_base64(annotated_frame)
            if base64_frame:
                send_detected_frame(channel_layer, base64_frame, detections)

            # Save detection data every 20 seconds
            if current_time - last_saved_time > 20:
                last_saved_time = current_time
                
                detectionWrite(base64_frame, detections, timezone.now())
                send_line_notify(base64_frame, len(detections.class_id), timezone.now())

        else:
            # Handle case with no detections
            
            base64_frame = encode_frame_as_base64(frame)
            if base64_frame:
                send_detected_frame(channel_layer, base64_frame, detections)

        


        # Throttle the frame rate
        time.sleep(1 / frame_rate)

    # Release video capture when done
    cap.release()


async def send_detected_frame(channel_layer, base64_frame, detections):
    timedetected = timezone.now()
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    local_time = timedetected.astimezone(bangkok_tz)
    formatted_datetime = local_time.strftime('%d %B %Y at %H:%M:%S')

    print("Sending frame with detected objects count:", len(detections.class_id))  # Debugging log

    try:
        await channel_layer.group_send(
            "video_stream",
            {
                "type": "video_frame",
                "frame": base64_frame,
                "found": len(detections.class_id),
                "time_detected": formatted_datetime,
            }
        )
    except Exception as e:
        print(f"Error sending frame: {e}")




def encode_frame_as_base64(frame):
    try:
        compress_rate = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # Reduce image quality for smaller size
        _, buffer = cv2.imencode('.jpg', frame, compress_rate)
        
        # _, buffer = cv2.imencode('.jpg', frame)
        
        return base64.b64encode(buffer).decode('utf-8')
    except Exception as e:
        print(f"Error encoding frame: {e}")
        return None


def detectionWrite(base64_frame, detections, time_detect):
    image_path = save_frame_image(base64_frame)
    from .models import LandsnailDetection, FrameDetection, Species

    frame_instance = FrameDetection(image=image_path, snail_detected=len(detections.class_id), time_detect=time_detect)
    frame_instance.save()

    for i in range(len(detections.xyxy)):
        class_name = detections.data['class_name'][i]
        conf_score = detections.confidence[i]
        species, created = Species.objects.get_or_create(name=class_name)

        detected_instance = LandsnailDetection(
            conf_score=conf_score,
            frame=frame_instance,
            species=species
        )
        detected_instance.save()


def save_frame_image(base64_frame):
    # Generate unique filename using timestamp
    timestamp = time.time()
    filename = f'frame_{timestamp}.jpg'

    # Construct the full path to the media directory
    media_directory = settings.MEDIA_ROOT
    frame_image_path = os.path.join(media_directory, 'frames_detected', filename)

    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(frame_image_path), exist_ok=True)
    
    # Decode base64 to image
    image_data = base64.b64decode(base64_frame)
    nparr = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Save the frame image
    cv2.imwrite(frame_image_path, img)

    return frame_image_path


def send_line_notify(base64_frame, detect_count, time_detect):
    line_notify_api = 'https://notify-api.line.me/api/notify'
    token = "CFQJre9DQJtRfZFLPIM8Td21MpkFP8BZ194EhNF7oh7"  # Replace with your token

    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Create message with detection count and time
    message = f'Detections: {detect_count}, Time Detected: {time_detect}'
    payload = {'message': message}

    # Prepare the image file
    files = {'imageFile': ('detection.jpg', base64.b64decode(base64_frame), 'image/jpeg')}
    
    # Send request with the image
    response = requests.post(line_notify_api, headers=headers, data=payload, files=files)
    print(f"LINE Notify response: {response.status_code}")



signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)