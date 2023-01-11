from .views import LoginAPIView,SignUpAPIView
from django.urls import path

urlpatterns = [
    path('login/',LoginAPIView.as_view(),name='login'),
    path('register/',SignUpAPIView.as_view(),name='register'),
]
