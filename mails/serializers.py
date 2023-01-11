from sqlite3 import Timestamp
from rest_framework import serializers
from datetime import datetime
from users.serializers import UserSerializer
from .models import Mail


class MailSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Mail
        fields = ['id', 'mail_from', 'mail_to', 'subject', 'body',
                  'timestamp', 'history_id', 'thread', 'user', 'created_at']
        read_only_fields = ['created_at']


