from __future__ import print_function
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from LiberalOverflow.models import UserProfile

# Import the email modules we'll need
from email.mime.text import MIMEText
import base64
import urllib

import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = tools.argparser.parse_args([])
except ImportError:
    flags = None

import uuid

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
SCOPES = 'https://mail.google.com'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'LiberalOverflow'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

    Returns:
    An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    print(message.as_string())
    raw = base64.urlsafe_b64encode(message.as_bytes())
    raw = raw.decode()
    return {'raw': raw}


def send_message(service, user_id, message):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

    Returns:
    Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: ' + message['id'])
        return message
    except urllib.error.HTTPError as error:
        print('An error occurred: ' + error)


# Create your views here.
def home(request):
    return render(request, 'home.html')


def register(request):
    print(request.get_raw_uri())
    return render(request, 'register.html')


def register_complete(request):
    # POST 파라미터 가져오기
    nickname = request.POST.get('nickname')
    password = request.POST.get('password')
    kaist_email = request.POST.get('email')
    auth_code = str(uuid.uuid4())

    # User object 만들기
    user = User.objects.create_user(nickname, kaist_email, password)
    user_profile = UserProfile()
    user_profile.user = user
    user_profile.authenticationCode = auth_code
    user_profile.save()

    # 인증 메일 보내기
    email_from = 'master.liberaloverflow@gmail.com'
    email_subject = 'LiberalOverflow Authentication Mail'
    email_content = 'Welcome, '+nickname+'!\n'+'Click the link below to authenticate your LiberalOverflow account.\n'
    email_content += 'http://localhost:8000/authenticate/' + nickname + '/' + auth_code
    email_msg = create_message(email_from, kaist_email, email_subject, email_content)
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    send_message(service, 'me', email_msg)

    # 완료 페이지 띄우기
    return render(request, 'register_complete.html')


def authenticate(request):
    request_url = request.get_raw_uri()
    request_url_list = request_url.split('/')
    nickname = request_url_list[-2]
    auth_code = request_url_list[-1]
    user = User.objects.get(username__exact=nickname)
    user_profile = user.userprofile
    if auth_code == user_profile.authenticationCode:
        # authentication success
        user_profile.isAuthenticated = True
        user_profile.save()
        return render(request, 'authentication_complete.html')
    else:
        # authentication fail
        return HttpResponse('Authentication fail')
