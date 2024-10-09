# urls.py
from django.urls import path
from .views import DetectionConfigurationView

urlpatterns = [
    path('', DetectionConfigurationView.as_view(), name='detection-configuration'),
]
