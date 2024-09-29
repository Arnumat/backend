from django.apps import AppConfig
# from .yolo_initialization import initialize_yolo_model

class StreamvideoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'streamvideo'


    # def ready(self):
    #     initialize_yolo_model()