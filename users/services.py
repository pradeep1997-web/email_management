import json
import os
from typing import Dict
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow


# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send']

class UserCredentials:
    def __init__(self,old_creds=None):
        self.old_creds =old_creds

    def get_credentials(self):
        creds = None
        if self.old_creds:
            creds = Credentials.from_authorized_user_info(self.old_creds,SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                creds = self.fetch_initial_credentials()
        return creds

    def get_credentials_json(self):
        creds = self.get_credentials()
        return creds.to_json()

    def fetch_initial_credentials(self):
        flow = InstalledAppFlow.from_client_secrets_file(
                    'users/credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        return creds


def update_credentials(user):
    if user:
        creds=None
        if user.credentials:
            creds = json.loads(user.credentials)
        credentials = UserCredentials(creds)
        new_creds = credentials.get_credentials_json()
        user.credentials = new_creds
        user.save()
        return user
