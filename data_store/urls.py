# from django.conf.urls import url
from django.urls import path, include
from .views import (
    DataStoreApiView,
    FileApiView,
    QuestionApiView  
)

urlpatterns = [
    path('data_store', DataStoreApiView.as_view()),
    path('question', QuestionApiView.as_view()),
    path('file/upload', FileApiView.as_view()),
]