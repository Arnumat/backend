# apps.py

# from django.apps import AppConfig
# from .detection_service import run_detection, shutdown_flag
# import threading
# import atexit


# class DetectionConfig(AppConfig):
#     name = 'detection'

    # def ready(self):
    #     # Fetch the configuration from the database
    #     config = DetectionConfiguration.objects.first()
    #     if config:
    #         from .models import DetectionConfiguration
    #         start_time = config.time_start
    #         end_time = config.time_end

    #         # Start the detection thread
    #         print("Starting detection thread...")
    #         self.detection_thread = threading.Thread(target=run_detection, args=(start_time, end_time))
    #         self.detection_thread.start()

    #         # Register the shutdown handler to stop the thread
    #         atexit.register(self.stop_detection_thread)

    # def stop_detection_thread(self):
    #     global shutdown_flag
    #     shutdown_flag = True  # Set the flag to stop the thread
    #     if self.detection_thread:
    #         print("Waiting for detection thread to stop...")
    #         self.detection_thread.join()  # Wait for the thread to finish
    #         print("Detection thread stopped.")


# apps.py

from django.apps import AppConfig
from .detection_service import run_detection, shutdown_flag
import threading
import atexit
import time

import datetime

class DetectionConfig(AppConfig):
    name = 'detection'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.detection_thread = None
        self.running = False  # Flag to track if the detection thread is running

    def ready(self):
        # Register the shutdown handler to stop the thread
        atexit.register(self.stop_detection_thread)
        
        # Start a separate thread to manage the detection timing
        self.management_thread = threading.Thread(target=self.manage_detection)
        self.management_thread.start()

    def manage_detection(self):
        from .models import DetectionConfiguration
        while True:
            config = DetectionConfiguration.objects.first()
            if config:
                start_time = config.time_start
                end_time = config.time_end
                current_time = datetime.datetime.now().time()

                # Start the detection thread if the current time is within the range and it's not already running
                if start_time <= current_time <= end_time and not self.running:
                    print("Starting detection thread...")
                    self.detection_thread = threading.Thread(target=run_detection, args=(start_time, end_time))
                    self.detection_thread.start()
                    self.running = True
                
                # Stop the detection thread if the current time is outside the range and it's running
                elif (current_time < start_time or current_time > end_time) and self.running:
                    print("Stopping detection thread...")
                    global shutdown_flag
                    shutdown_flag = True  # Set the flag to stop the thread
                    self.detection_thread.join()  # Wait for the thread to finish
                    self.detection_thread = None  # Reset the thread
                    self.running = False

            time.sleep(60)  # Check every minute

    def stop_detection_thread(self):
        global shutdown_flag
        shutdown_flag = True  # Set the flag to stop the thread
        if self.detection_thread:
            print("Waiting for detection thread to stop...")
            self.detection_thread.join()  # Wait for the thread to finish
            print("Detection thread stopped.")
