
# from django.conf.urls import url
from django.urls import path, include
from .views import (
    ChatbotApiView,
    StatsApiView,
    ChatbotDetailsApiView,
    LogoApiView,
    serve_static_file
)

urlpatterns = [
    path('chatbots', ChatbotApiView.as_view()),
    path('logo/upload', LogoApiView.as_view()),
    path('chatbots/details/', ChatbotDetailsApiView.as_view()),
    path('stats', StatsApiView.as_view()),
    path('static-files/<str:file_name>/', serve_static_file, name='serve_static_file'),

]