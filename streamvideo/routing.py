from django.conf import settings
from django.urls import re_path
from . import consumers
from django.conf.urls.static import static


websocket_urlpatterns = [
    re_path(r'ws/video_stream/$', consumers.VideoStreamConsumer.as_asgi()),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
