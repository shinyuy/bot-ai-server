
# from django.conf.urls import url
from django.urls import path, include
from .views import (
    CompanyApiView,
)

urlpatterns = [
    path('company', CompanyApiView.as_view()),
]