from rest_framework import serializers
from .models import Species, FrameDetection, LandsnailDetection
import base64
class SpeciesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Species
        fields = ['id', 'name'] 

class FrameDetectionSerializer(serializers.ModelSerializer):
    image_base64 = serializers.SerializerMethodField()
    class Meta:
        model = FrameDetection
        fields = ['id', 'image_base64', 'snail_detected', 'time_detect']

    def get_image_base64(self, obj):
        with open(obj.image.path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

class LandsnailDetectionSerializer(serializers.ModelSerializer):
    species = SpeciesSerializer()  
    frame = FrameDetectionSerializer() 

    class Meta:
        model = LandsnailDetection
        fields = ['id', 'species', 'frame', 'conf_score']
