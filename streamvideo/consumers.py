from channels.generic.websocket import AsyncWebsocketConsumer
import json

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the group
        await self.channel_layer.group_add(
            "video_stream",
            self.channel_name
        )
        await self.accept()
        print(f"{self.channel_name} connected to the video stream.")

    async def disconnect(self, close_code):
        # Leave the group
        await self.channel_layer.group_discard(
            "video_stream",
            self.channel_name
        )
        print(f"{self.channel_name} disconnected from the video stream.")
    
    


    # Receive a message from the group
    async def video_frame(self, event):
        # Extract data from the event
        base64_frame = event['base64_frame']
        found = event['found']
        time_detected = event['time_detected']

        # Send the frame and data to WebSocket
        await self.send(text_data=json.dumps({
            'frame': base64_frame,  # Sending the base64 encoded frame
            'found': found,
            'time_detected': time_detected,
        }))
