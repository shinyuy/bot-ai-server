# from django.conf.urls import url
from django.urls import path, include
from .views import (
    TwilioCallWebhooksApiView,
)

urlpatterns = [
    path('twilio/webhook', TwilioCallWebhooksApiView.as_view()),
]