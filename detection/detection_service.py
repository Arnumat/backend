import os
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

# Global shutdown flag
shutdown_flag = False

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    global shutdown_flag
    print("Shutdown signal received.")
    shutdown_flag = True



def run_detection():
    from detection_config.models import DetectionConfiguration
    global shutdown_flag
    
    # CAMERA_INDEX = "http://192.168.112.36:5000/video_feed"  # Your video feed URL
    CAMERA_INDEX = 0  # Your video feed URL
    
    DETECTED_COUNT = 0
    SEQUENCE_TIME_INSERT_SEC = 60
    SEQUENCE_TIME_NOTIFY_SEC = 60
    

    # Load the YOLO model
    model = get_yolo_model()
    
    # Initialize the tracker and annotators
    tracker = sv.ByteTrack()
    trace_annotator = sv.TraceAnnotator()
    # bounding_box_annotator = sv.BoundingBoxAnnotator()
    bounding_box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    # Set up the Django Channels layer
    channel_layer = get_channel_layer()
    
    # Open the video capture
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    print("Video source opened successfully.")

    frame_rate = 20  # Frame rate control
    last_saved_time = time.time()
    last_notify_time = time.time()
    
    
    while not shutdown_flag:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to read frame from video source.")
            break

        # Run the YOLO model to detect objects
        results = model(frame, verbose=False)[0]
        detections = sv.Detections.from_ultralytics(results)
        detections = tracker.update_with_detections(detections)
        DETECTED_COUNT = len(detections.class_id)
        current_time = time.time()
        
        if DETECTED_COUNT > 0:
            
            if detections.tracker_id.size > 0:
                labels = [f"{class_name} #{tracker_id}" for class_name,tracker_id in zip(detections.data['class_name'],detections.tracker_id)]
                annotated_frame = label_annotator.annotate(scene=frame.copy(), detections=detections, labels=labels)
                annotated_frame = trace_annotator.annotate(scene=annotated_frame, detections=detections)
            else: 
                annotated_frame = label_annotator.annotate(scene=frame.copy(), detections=detections)
                
            annotated_frame = bounding_box_annotator.annotate(scene=annotated_frame, detections=detections)

            # Encode the annotated frame to base64    
            result_base64_frame = encode_frame_as_base64(annotated_frame)
            
            # Send the result frame to WebSocket
            send_detected_frame(channel_layer, result_base64_frame, detections)
                    
            config = DetectionConfiguration.objects.last()
            SEQUENCE_TIME_INSERT_SEC = config.sequence_insert_data      
            SEQUENCE_TIME_NOTIFY_SEC = config.sequence_notify
            if (current_time - last_saved_time )> (SEQUENCE_TIME_INSERT_SEC * 60):
                # Save detection data every SEQUENCE_TIME_SEC seconds
                last_saved_time = current_time
                formatted_time = conv_time_format(timezone.now())
                detectionWrite(result_base64_frame, detections, timezone.now())
                print('detection save signal')

            if (current_time - last_notify_time )> (SEQUENCE_TIME_NOTIFY_SEC * 60):
                # Save detection data every SEQUENCE_TIME_SEC seconds
                last_notify_time = current_time
                # formatted_time = conv_time_format(timezone.now())
                detectionWrite(result_base64_frame, detections, timezone.now())
                
                print('detection notify signal')
            
                send_line_notify(result_base64_frame, len(detections.class_id), formatted_time)
            
            DETECTED_COUNT = 0
            
        else:
            # If no detection, send the original frame
            result_base64_frame = encode_frame_as_base64(frame.copy())
            send_detected_frame(channel_layer, result_base64_frame, detections)

        # Throttle the frame rate
        time.sleep(1 / frame_rate)

    # Release the video capture resource when exiting
    cap.release()
   

def send_detected_frame(channel_layer, base64_frame, detections):
    time_detected = conv_time_format(timezone.now())


    try:
        async_to_sync(channel_layer.group_send)(
            "video_stream",
            {
                "type": "video_frame",
                "base64_frame": base64_frame,
                "found": len(detections.class_id),
                "time_detected": time_detected
            }
        )
    except Exception as e:
        print(f"Error sending frame: {e}")

def conv_time_format(time_detect):
    # Convert the `time_detect` to a string in the desired format
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    local_time = time_detect.astimezone(bangkok_tz)
    formatted_time = local_time.strftime('%H:%M:%S')
    return formatted_time

def encode_frame_as_base64(frame, width=640):
    try:
        # Resize the frame to maintain aspect ratio
        height = int(frame.shape[0] * width / frame.shape[1])
        resized_frame = cv2.resize(frame, (width, height))

        # Compress the image to reduce size
        compress_rate = [int(cv2.IMWRITE_JPEG_QUALITY), 50]  # Set JPEG quality to 50%
        success, buffer = cv2.imencode('.jpg', resized_frame, compress_rate)

        if not success:
            print("Error: Frame encoding failed.")
            return None

        # Encode the buffer to base64
        base64_image = base64.b64encode(buffer).decode('utf-8')
        return base64_image
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
    time_detect = timezone.now()
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    local_time = time_detect.astimezone(bangkok_tz)
    formatted_time = local_time.strftime('%d_%B_%Y-%H_%M_%S')
    filename = f'frame_{formatted_time}.jpg'

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
    token = "Kn1CApJcYg82FtGzxz9kS94VGfNM18fcuDXTdvDC05X"  # Replace with your token

    headers = {
        'Authorization': f'Bearer {token}'
    }

    # Create message with detection count and time
    message = (
        f"🚨 *Detection Alert!* 🚨\n\n"
        f"🔍 **Found:** {detect_count} land snails detected.\n"
        f"🕒 **Time Detected:** {time_detect}\n"
        f"📸 An image is attached below."
    )
    payload = {'message': message}

    # Prepare the image file
    files = {'imageFile': ('detection.jpg', base64.b64decode(base64_frame), 'image/jpeg')}
    
    # Send request with the image
    response = requests.post(line_notify_api, headers=headers, data=payload, files=files)
  


# Register signal handlers for SIGINT and SIGTERM
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)