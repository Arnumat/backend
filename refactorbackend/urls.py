from django.contrib import admin
from django.urls import path , include
from .view import login , signup
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/login',login),
    path('auth/signup',signup),
    path('',include('landsnail.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
