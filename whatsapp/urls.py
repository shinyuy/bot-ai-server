# from django.conf.urls import url
from django.urls import path, include
from .views import (
    WhatsAppApiView 
)

urlpatterns = [
    path('whatsapp', WhatsAppApiView.as_view()),
]


# speechrecognition==3.9.0
# soundfile==0.12.1
# pydub==0.25.1