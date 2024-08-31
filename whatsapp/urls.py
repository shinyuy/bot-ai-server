# from django.conf.urls import url
from django.urls import path, include
from .views import (
    WhatsAppApiView 
)

urlpatterns = [
    path('whatsapp', WhatsAppApiView.as_view()),
]