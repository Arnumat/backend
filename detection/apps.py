from django.apps import AppConfig
from .detection_service import run_detection, shutdown_flag
import threading
import atexit

class DetectionConfig(AppConfig):
    name = 'detection'
    
    def ready(self):
        # Start the detection thread
        print("starting thread")
        self.detection_thread = threading.Thread(target=run_detection)
        self.detection_thread.start()

        # Register the shutdown handler to stop the thread
        atexit.register(self.stop_detection_thread)

    def stop_detection_thread(self):
        global shutdown_flag
        shutdown_flag = True  # Set the flag to stop the thread
        if self.detection_thread:
            print("Waiting for detection thread to stop...")
            self.detection_thread.join()  # Wait for the thread to finish
            print("Detection thread stopped.")
