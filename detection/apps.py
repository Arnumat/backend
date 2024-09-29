from django.apps import AppConfig
from .detection_service import run_detection
import threading

class DetectionConfig(AppConfig):
    # default_auto_field = 'django.db.models.BigAutoField'
    name = 'detection'


    def ready(self):

        threading.Thread(target=run_detection).start()