
# from django.conf.urls import url
from django.urls import path, include
from .views import (
    ChatbotApiView,
    StatsApiView,
    ChatbotDetailsApiView
)

urlpatterns = [
    path('chatbots', ChatbotApiView.as_view()),
    path('chatbots/details/', ChatbotDetailsApiView.as_view()),
    path('stats', StatsApiView.as_view()),
]