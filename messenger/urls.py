# from django.conf.urls import url
from django.urls import path, include
from .views import (
    MessengerApiView 
)

urlpatterns = [
    path('messenger', MessengerApiView.as_view()),
]

