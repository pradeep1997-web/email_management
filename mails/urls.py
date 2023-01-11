from django.urls import path
from .views import SendMail, SyncMail

urlpatterns = [
    path('sync/',SyncMail.as_view(),name='sync_mail'),
    path('send_mail/',SendMail.as_view(),name='send_mail')
]
