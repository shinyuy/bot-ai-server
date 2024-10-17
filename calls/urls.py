# from django.conf.urls import url
from django.urls import path, include
from .views import (
    CallsApiView,
)

urlpatterns = [
    # path('ws/calls/', CallsApiView.as_view()),
]