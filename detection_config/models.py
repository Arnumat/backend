from django.db import models

# models.py
class DetectionConfiguration(models.Model):
    time_start = models.TimeField()
    time_end = models.TimeField()
    sequence_notify = models.IntegerField()
    sequence_insert_data = models.IntegerField()

    def __str__(self):
        return f'Config: {self.time_start} - {self.time_end}'
