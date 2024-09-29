from django.contrib import admin

# Register your models here.
from .models import Species , FrameDetection , LandsnailDetection
# Register your models here.
admin.site.register(Species)
admin.site.register(FrameDetection)
admin.site.register(LandsnailDetection)
