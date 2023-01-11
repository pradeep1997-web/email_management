from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64
import time
from .models import Mail
from users.services import UserCredentials
import json
import datetime


class MailOperation:
    def __init__(self, credentials, query=''):
        self.credentials = credentials
        self.query = query

    def service(self):
        return build('gmail', 'v1', credentials=self.credentials)

    def get_mail_list_from_page(self, next_page):
        try:
            mails = []

            messages = self.service().users().messages().list(
                userId='me', q=self.query, pageToken=next_page).execute()
            mails = messages.get('messages')
            next_page = messages.get('nextPageToken', '')
            # all_mails += mails
            # print(mails)

            return mails, next_page
        except HttpError as error:
            print('An error occurred: %s' % error)
            return "Error"

    def get_mail(self, mail_id):
        try:
            message_data = self.service().users().messages().get(
                userId='me', id=mail_id).execute()
            time.sleep(1)
            return message_data
        except HttpError as error:
            print('An error occurred: %s' % error)
            return "Error"

    def get_thread(self, mail_id):
        try:
            thread_data = self.service().users().thread().get(
                userId='me', id=mail_id).execute()
            return thread_data
        except HttpError as error:
            print('An error occurred: %s' % error)
            return "Error"

    def create_message(self, sender, to, subject, msgHtml, msgPlain):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to
        msg.attach(MIMEText(msgPlain, 'plain'))
        msg.attach(MIMEText(msgHtml, 'html'))
        return {'raw': base64.urlsafe_b64encode(msg.as_bytes())}

    def create_reply_message(self, sender, to, message_id, thread_id, subject, message_text):
        message = MIMEText(message_text)
        message['From'] = sender
        message['To'] = to
        message['In-Reply-To'] = message_id
        message['References'] = message_id
        message['Subject'] = subject

        return {
            'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode(),
            'threadId': thread_id
        }

    def send_mail(self, sender, to, subject, msgHtml, msgPlain):
        try:
            message = self.create_message(
                sender, to, subject, msgHtml, msgPlain)
            message = self.service().users().messages().send(userId='me', body=message)
            print("Message with {0} sent.".format(message['id']))
            return message
        except HttpError as error:
            print('An error occurred: %s' % error)
            return "Error"

    def reply_mail(self, sender, to, message_id, thread_id, subject, message_text):
        try:
            message = self.create_reply_message(
                sender, to,message_id,thread_id, subject,message_text)
            sent_message = self.service().users().messages().send(userId='me', body=message)
            print(message)
            print(sent_message)
            # print("Reply to {0} by message {1}".format(message['threadId'],message['id']))
            return sent_message
        except HttpError as error:
            print('An error occurred: %s' % error)
            return "Error"


def fetch_mail_list(credentials, query_params,last_id):
    mail_obj = MailOperation(credentials, query=query_params)
    mails, next_page = mail_obj.get_mail_list_from_page('')
    # print("mails",mails)
    unsynced_mail_ids = list()
    unsynced_threads = list()
    for mail in mails:
        # print(mail['id'])
        unsynced_mail_ids.append(mail['id'])  # type: ignore
        unsynced_threads.append(mail['threadId'])  # type: ignore
        if mail['id'] == last_id:  # type: ignore
            break

    unsynced_mail_ids = unsynced_mail_ids[::-1]
    print("unsynced_mail_ids", unsynced_mail_ids)
    unsynced_threads = unsynced_threads[::-1]
    return unsynced_mail_ids, unsynced_threads, next_page


def sync_mail(user, credentials, query_params, id, threadId, mail):
    mail_obj = MailOperation(credentials, query_params)
    if mail == None:
        new_mail = mail_obj.get_mail(id)
        new_mail_obj = Mail()
        new_mail_obj.id = id
        new_mail_obj.user = user
        new_mail_obj.history_id = new_mail['historyId']  # type: ignore
        new_mail_obj.timestamp = new_mail['internalDate']  # type: ignore
        new_mail_obj.body = new_mail['snippet']  # type: ignore
        mail_data = new_mail['payload']['headers']  # type: ignore
        for data in mail_data:
            name = data['name']  # type: ignore
            if name == 'From':
                new_mail_obj.mail_from = data['value']  # type: ignore
            if name == 'To':
                # print(data['value'])
                new_mail_obj.mail_to = data['value']  # type: ignore
            if name == 'Subject':
                new_mail_obj.subject = data['value']  # type: ignore
        new_mail_obj.thread = threadId
        print('thread', threadId)
        new_mail_obj.save()
    else:
        new_mail_obj = Mail.objects.get(id=mail.id)
    return new_mail_obj.id


def sync_mails(user, last_mail=None):
    '''
    Function requires last synced email and fetch unsync emails after the obtained mail and sync with the database
    '''
    # print(json.loads(user.credentials))
    credentials = UserCredentials(
        json.loads(user.credentials)).get_credentials()
    # print(credentials.to_json())
    query_params = ''
    last_id = ''
    if last_mail:
        last_id = last_mail.id
        last_date = datetime.datetime.utcfromtimestamp(
            int(last_mail.timestamp)/1000).strftime('%Y-%m-%d')
        query_params = 'after:'+last_date
    unsynced_mail_ids, unsynced_threads, next_page = fetch_mail_list(
        credentials=credentials, query_params=query_params,last_id=last_id)
    if len(unsynced_mail_ids) > 0:  # type: ignore
        for (id, threadId) in zip(unsynced_mail_ids, unsynced_threads):  # type: ignore
            # pprint.pprint(new_mail)
            # print('id----', id)
            try:
                mail = Mail.objects.get(id=id)
                continue
            except Mail.DoesNotExist:
                mail = None
            new_mail_id = sync_mail(
                user, credentials, query_params, id, threadId, mail)
