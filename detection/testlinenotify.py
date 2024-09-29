
import requests


def send_line_notify(frame_byte, detect_count, time_detect):
    """
    Send a message with an image to LINE Notify.

    :param image_bytes: The image bytes to send.
    :param detect_count: The count of detections.
    :param time_detect: The time of detection.
    :param token: Your LINE Notify access token.
    :return: Response from LINE Notify.
    """
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
    # files = {'imageFile': ('detection.jpg', frame_byte, 'image/jpeg')}
    
    # response = requests.post(line_notify_api, headers=headers, data=payload, files=files)
    
    response = requests.post(line_notify_api, headers=headers, data=payload)
    
    return response