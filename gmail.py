import pickle
import os
import os.path
import base64
import datetime as dt
from email.mime.text import MIMEText

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from config import Config


SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']

MAIL_FROM = Config.MAIL_FROM
MAIL_TO = Config.MAIL_TO

last_mail_update = int(dt.datetime.now().timestamp())

old_msg_set = {}
new_msg_set = {}

def get_or_refresh_service():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message_api(service, message, user_id='me'):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                    .execute())
        print('Message Id: %s' % message['id'])
        return message
    except HttpError as error:
        print('An error occurred: %s' % error)


def send_message(text):
    service = get_or_refresh_service()
    message = create_message(MAIL_FROM, MAIL_TO, 'Message to SMS', text)
    send_message_api(service, message)


def recieve_messages_api(service, after, user_id='me'):
    try:
        messages = {}

        iter_messages = (service.users().messages().list(userId=user_id, q=f'from:{Config.MAIL_TO} after:')
                    .execute()).get('messages', [])
        
        for msg in iter_messages:
            msg_object = (service.users().messages().get(userId=user_id, id=msg['id'])
                    .execute())
            msg_body_base64 = msg_object['payload']['parts'][0]['body']['data']
            msg_body_ascii = msg_body_base64.encode('ascii')
            msg_body_plain = base64.b64decode(msg_body_ascii)
            msg_body_decoded = msg_body_plain.decode('utf8').strip()
            messages[msg['id']] = msg_body_decoded

        return messages
    except HttpError as error:
        print('An error occurred: %s' % error)

def recieve_messages():
    global last_mail_update
    global old_msg_set
    global new_msg_set

    service = get_or_refresh_service()
    tmp = int(dt.datetime.now().timestamp())
    messages = recieve_messages_api(service, last_mail_update)
    last_mail_update = tmp

    new_msg_set = messages.keys()
    unsend_msg_set = new_msg_set - old_msg_set
    old_msg_set = new_msg_set

    unsend_messages = []
    for msg_id in unsend_msg_set:
        unsend_messages.append(messages[msg_id])

    return unsend_messages


for msg in recieve_messages():
    print(msg)