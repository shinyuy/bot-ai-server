# from django.conf.urls import url
from django.urls import path, include
from .views import (
    DataStoreApiView,
    FileApiView,
    QuestionApiView,
    DataStoreAllApiView
)

urlpatterns = [
    path('data_store', DataStoreApiView.as_view()),
    path('data_store/all', DataStoreAllApiView.as_view()),
    path('question', QuestionApiView.as_view()),
    path('file/upload', FileApiView.as_view()),
]