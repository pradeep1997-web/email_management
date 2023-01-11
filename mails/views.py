from mails.serializers import MailSerializer
from users.services import UserCredentials
from .models import Mail
from users.models import CustomUser
from .services import MailOperation, fetch_mail_list, sync_mail,sync_mails
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from upwards.utils import CustomPagination
import json
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_list_or_404
import pprint
# Create your views here.


class SyncMail(GenericAPIView):
    serializer_class = MailSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    queryset = Mail.objects.all()
    pagination_class = CustomPagination

    def get_queryset(self):
        return Mail.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwars):
        mail = self.get_queryset().order_by('-created_at')
        if mail:
            last_mail = mail[0]
            print("last_mail", last_mail.id)
            sync_mails(user=request.user, last_mail=last_mail)
        else:
            sync_mails(user=request.user, last_mail=None)
        mails = Mail.objects.filter(
            user=self.request.user).order_by('-created_at')
        serializer = MailSerializer(mails, many=True)
        data = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(data)

    def get(self, request, *args, **kwars):
        mails = self.get_queryset().order_by('-created_at')
        serializer = MailSerializer(mails, many=True)
        data = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(data)


class SendMail(GenericAPIView):
    serializer_class = MailSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def get_queryset(self):
        # type: ignore
        return Mail.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        data = request.data
        user = CustomUser.objects.get(id=request.user.id)
        credentials = UserCredentials(
            json.loads(user.credentials)).get_credentials()
        from_mail = data.get('from', '')
        query = ''
        if from_mail != '':
            query = 'from:'+from_mail
        mail_list, mail_treads, next = fetch_mail_list(
            credentials=credentials, query_params=query,last_id='')
        if len(mail_list) > 0:
            mails = list()
            for (id, threadId) in zip(mail_list, mail_treads):
                try:
                    mail = Mail.objects.get(id=id)
                except Mail.DoesNotExist:
                    mail = None
                new_thread_id = sync_mail(
                    user, credentials, query, id, threadId, mail)
                print("new_thread_id",new_thread_id)
                mails.append(new_thread_id)
            if len(mails) > 0:
                queryset = get_list_or_404(Mail, id__in=mails)
                print("queryset",queryset)
                for mail in queryset:
                    if "Please Help Me!" in mail.body:  # type: ignore
                        mail_obj = MailOperation(
                            credentials, query='')
                        print(mail.id,mail.mail_from,mail.mail_to)
                        reply = mail_obj.reply_mail(sender=mail.mail_to, to=mail.mail_from, message_id=mail.id, thread_id=mail.id,
                                                    subject="HI", message_text="Hello There, We will get back to you on this.")
                        pprint.pprint(reply)
                        return Response({"data": "Sent mail", 'id': 'id'}, status=status.HTTP_200_OK) #type: ignore

            return Response({"data": "No mail found", }, status=status.HTTP_404_NOT_FOUND)
