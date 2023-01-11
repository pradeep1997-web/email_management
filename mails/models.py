#from msilib.schema import CustomAction
from unittest.util import _MAX_LENGTH
from django.db import models
from users.models import CustomUser
from django.utils.translation import gettext_lazy as _
# Create your models here.


class Mail(models.Model):
    id = models.CharField(primary_key=True, max_length=11, unique=True)
    mail_from = models.CharField(max_length=255, null=True, blank=True)
    mail_to = models.CharField(max_length=255, null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    subject = models.CharField(
        _("Subject"), max_length=255, null=True, blank=True)
    history_id = models.CharField(_("History ID"), max_length=128)
    timestamp = models.CharField(max_length=65, null=True, blank=True)
    # thread_id = models.ForeignKey("self", on_delete=models.CASCADE,related_name='mail_treads')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='user_mails')
    thread = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.id
