from channels.generic.websocket import AsyncWebsocketConsumer
import base64
import json

class VideoStreamConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join the video stream group
        await self.channel_layer.group_add("video_stream", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the video stream group
        await self.channel_layer.group_discard("video_stream", self.channel_name)

    async def send_frame(self, frame, found, time_detected):
        frame_bytes = base64.b64encode(frame).decode('utf-8')
        await self.channel_layer.group_send(
            "video_stream",
            {
                "type": "video_frame",
                "frame": frame_bytes,
                "found": found,
                "time_detected": time_detected
            }
        )

    async def video_frame(self, event):
        await self.send(text_data=json.dumps({
            "type": "video_frame",
            "frame": event["frame"],
            "found": event['found'],
            "time_detected": event['time_detected']
        }))


    