from rest_framework import generics, status
from rest_framework.response import Response
from .models import DetectionConfiguration
from .serializers import DetectionConfigurationSerializer

class DetectionConfigurationView(generics.ListCreateAPIView):
    queryset = DetectionConfiguration.objects.all()
    serializer_class = DetectionConfigurationSerializer

    def post(self, request):
        serializer = DetectionConfigurationSerializer(data=request.data)
        if serializer.is_valid():
            # Save the configuration data
            serializer.save()
            return Response({'message': 'Configuration applied successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        config_data = self.get_queryset().last()  # Fetch the most recent entry
        if config_data:
            serializer = self.get_serializer(config_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'message': 'No configuration found.'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request):
        config_data = self.get_queryset().last()  # Fetch the most recent entry
        if config_data:
            serializer = self.get_serializer(config_data, data=request.data, partial=True)  # Allow partial updates
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Configuration updated successfully!'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'No configuration found.'}, status=status.HTTP_404_NOT_FOUND)
