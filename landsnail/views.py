from rest_framework import viewsets
from .models import Species , FrameDetection , LandsnailDetection
from .serializer import SpeciesSerializer , FrameDetectionSerializer , LandsnailDetectionSerializer
# Create your views here.
class SpeciesViewSet(viewsets.ModelViewSet):
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer
    
    
class FrameDetectionViewSet(viewsets.ModelViewSet):
    queryset = FrameDetection.objects.all()
    serializer_class = FrameDetectionSerializer
    
    
class LandsnailDetectionViewSet(viewsets.ModelViewSet):
    queryset = LandsnailDetection.objects.select_related('species', 'frame').all()
    serializer_class = LandsnailDetectionSerializer