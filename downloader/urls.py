from django.urls import path
from .views import descargar_video

urlpatterns = [
    path('descargar/', descargar_video),
]