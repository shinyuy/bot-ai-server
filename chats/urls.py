
# from django.conf.urls import url
from django.urls import path, include
from .views import (
    ChatApiView,
)

urlpatterns = [
    path('chats', ChatApiView.as_view()),
]