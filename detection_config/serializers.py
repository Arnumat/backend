# serializers.py
from rest_framework import serializers
from .models import DetectionConfiguration

class DetectionConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionConfiguration
        fields = '__all__'
