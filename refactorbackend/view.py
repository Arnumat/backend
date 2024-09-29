
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.decorators import authentication_classes , permission_classes
from rest_framework.authentication import SessionAuthentication , TokenAuthentication 
from rest_framework.permissions import IsAuthenticated



@api_view(['POST'])
def signup(request):
    serializer = UserSerializer(data= request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"user":serializer.data,"token":token.key},status=status.HTTP_201_CREATED)
    return Response(serializer.errors,status= status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login(request):
    user = get_object_or_404(User,username= request.data['username'])
    if not user.check_password(request.data['password']):
        return Response({'detail':"Not found."},status=status.HTTP_404_NOT_FOUND)
    token,created =Token.objects.get_or_create(user=user)
    serializer = UserSerializer(instance=user)
    return Response({"user":serializer.data,"token":token.key})



@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout(request):
    # The request user will already be authenticated due to TokenAuthentication
    user = request.user

    # Delete the token to log the user out
    try:
        token = Token.objects.get(user=user)
        token.delete()
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({"detail": "Invalid token or user not authenticated."}, status=status.HTTP_400_BAD_REQUEST)