import base64
import json
import time
import cv2
import numpy as np
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "video_stream_group",
            self.channel_name
        )
        await self.accept()

        # Start a background task to fetch and process frames
        self.video_stream_task = asyncio.create_task(self.fetch_and_process_frames())

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "video_stream_group",
            self.channel_name
        )
        if hasattr(self, 'video_stream_task'):
            self.video_stream_task.cancel()

    async def fetch_and_process_frames(self):
        url = 'http://localhost:1234/video'  # Replace with the IP address of your Raspberry Pi
        cap = cv2.VideoCapture(url)
        
        if not cap.isOpened():
            print("Error: Unable to open video stream.")
            return
        
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to read frame.")
                break

            # Process the frame (for testing, we just save it and broadcast it)
            annotated_image = await self.process_frame(frame)
            
            # Send the frame to clients
            await self.send_frame_to_clients(annotated_image)

            # Sleep for a short period to avoid excessive CPU usage
            # await asyncio.sleep(0.1)

        cap.release()

    async def send_frame_to_clients(self, frame):
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        await self.channel_layer.group_send(
            "video_stream_group",
            {
                'type': 'video_frame',
                'frame': base64.b64encode(frame_bytes).decode('utf-8')
            }
        )

    async def video_frame(self, event):
        await self.send(text_data=json.dumps({
            'type': 'video_frame',
            'frame': event['frame']
        }))

    async def process_frame(self, frame):
        # For testing purposes, save the frame to a file
        # timestamp = time.time()
        # frame_image_path = f'frame_{timestamp}.jpg'
        # cv2.imwrite(frame_image_path, frame)

        # Return the frame as-is for broadcasting
        return frame
