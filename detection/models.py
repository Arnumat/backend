from django.db import models
from django.utils import timezone
import pytz
# Create your models here.
class Species(models.Model):
    name = models.CharField(max_length=25)
    
    def __str__(self):
        return self.name
    
    
class FrameDetection(models.Model):
    image = models.ImageField(upload_to='images/detected')
    snail_detected = models.IntegerField()
    time_detect = models.DateTimeField(default = timezone.now)
    

    def __str__(self):
        bangkok_tz = pytz.timezone('Asia/Bangkok')
        local_time = self.time_detect.astimezone(bangkok_tz)
        formatted_date = local_time.strftime('%d %B %Y at time %H:%M:%S')
        
        return f"Frame {self.snail_detected} at {formatted_date}"
    

class LandsnailDetection(models.Model):
    species = models.ForeignKey(Species,on_delete= models.CASCADE)
    conf_score = models.FloatField()
    frame = models.ForeignKey(FrameDetection,on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.species.name} at frame ID : {self.frame.id}'
    