from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import SpeciesViewSet , FrameDetectionViewSet ,LandsnailDetectionViewSet



router = DefaultRouter()

router.register(r'species',SpeciesViewSet)
router.register(r'frame-detections',FrameDetectionViewSet)
router.register(r'landsnail-detections',LandsnailDetectionViewSet)


urlpatterns = [
    path('data/',include(router.urls))
]