from __future__ import print_function
from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from LiberalOverflow.models import UserProfile, Lecture, TimeSlot, Chat, ChatMessage
from django.contrib.auth.decorators import login_required

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
import json


import logging


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


def find_take_lectures(my_profile, your_profile):
    take_lectures = []
    your_lectures = list(your_profile.taken_lectures.all())
    my_wishes = list(my_profile.wish_time_slots.all())
    for lec in your_lectures:
        if lec.time_slots.all()[0] in my_wishes:
            take_lectures.append(lec)
    return take_lectures


def find_give_lectures(my_profile, your_profile):
    give_lectures = []
    my_lectures = list(my_profile.taken_lectures.all())
    your_wishes = list(your_profile.wish_time_slots.all())
    for lec in my_lectures:
        if lec.time_slots.all()[0] in your_wishes:
            give_lectures.append(lec)
    return give_lectures


# Create your views here.
def home(request):
    # matching algorithm
    context = {}
    if request.user.is_authenticated:
        my_profile = UserProfile.objects.filter(user=request.user)[0]
        user_profile_all = list(UserProfile.objects.exclude(user=request.user))
        exchangables = []
        notifications = []
        for notification in my_profile.notifications.all():
            notifications.append([notification.chatter, notification.message])
        for user_profile in user_profile_all:
            take_lectures = find_take_lectures(my_profile, user_profile)
            give_lectures = find_give_lectures(my_profile, user_profile)
            if take_lectures or give_lectures:
                exchangables.append([user_profile.user.username, take_lectures, give_lectures])
        context = {
            'exchangables': exchangables,
            'notifications': notifications
        }
    return render(request, 'home.html', context)


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


def my_authenticate(request):
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
        login(request, user)
        return render(request, 'authentication_complete.html')
    else:
        # authentication fail
        return HttpResponse('Authentication fail')


def my_login_ajax(request):
    print(request)
    username = request.POST['nickname']
    password = request.POST['password']
    response_data = {}
    user = authenticate(username=username, password=password)
    if user is not None:
        login(request, user)
        # Redirect to a success page.
        response_data['nickname'] = username
        response_data['success'] = True
    else:
        # Return an 'invalid login' error message.
        response_data['nickname'] = username
        response_data['success'] = False
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def my_login(request):
    return render(request, 'login.html')


def my_logout(request):
    if request.user.is_authenticated():
        logout(request)
    return redirect('/')


def check_duplicate_ajax(request):
    username = request.POST['nickname']
    response_data = {}
    if User.objects.filter(username=username).exists():
        response_data['is_duplicate'] = True
    else:
        response_data['is_duplicate'] = False
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required(login_url='/login/')
def timetable(request):
    user_profile = UserProfile.objects.get(user=request.user)
    # fetch time table and render.
    lectures = list(Lecture.objects.all())
    taken_lectures = list(user_profile.taken_lectures.all())
    wish_time_slots = list(user_profile.wish_time_slots.all())
    wish_time_slots_class = [slot.day_of_week + str(slot.start_time) for slot in wish_time_slots]
    lecture_infos = []
    for lecture in lectures:
        if lecture in taken_lectures:
            is_taken = 1
        else:
            is_taken = 0
        lecture_infos.append([lecture.lecture_name, lecture.professor_name, lecture.time_slots.all()[0].day_of_week + str(lecture.time_slots.all()[0].start_time), is_taken])
    context = {
        'lecture_infos': lecture_infos,
        'wish_time_slots_class': wish_time_slots_class
    }
    return render(request, 'timetable.html', context)


def add_taken_ajax(request):
    taken_lecture_name = request.POST['taken_lecture_name']
    response_data = {}
    taken_lecture = Lecture.objects.filter(lecture_name=taken_lecture_name)[0]
    # add lecture to user timetable ##########
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.taken_lectures.add(taken_lecture)
    user_profile.save()
    ##########################################
    response_data['success'] = True
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def delete_taken_ajax(request):
    taken_lecture_name = request.POST['taken_lecture_name']
    response_data = {}
    taken_lecture = Lecture.objects.filter(lecture_name=taken_lecture_name)[0]
    #################################
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.taken_lectures.remove(taken_lecture)
    user_profile.save()
    #################################
    response_data['success'] = True
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def add_wish_ajax(request):
    response_data = {}
    wish_time_slot_class = request.POST['wish_time_slot']
    wish_time_slot_parsed = wish_time_slot_class.split('y')
    wish_dow = wish_time_slot_parsed[0] + 'y'
    wish_start_time = float(wish_time_slot_parsed[1])
    wish_time_slot = TimeSlot.objects.filter(day_of_week=wish_dow, start_time=wish_start_time)[0]
    # add lecture to user timetable ##########
    user_profile = UserProfile.objects.get(user=request.user)
    # delete와 아래의 한줄만 다르므로 리팩토링이 가능하다. 클라 단에서 아작스 리퀘스트 보낼 때 불리언 필드 하나 던져서.
    user_profile.wish_time_slots.add(wish_time_slot)
    user_profile.save()
    ##########################################
    response_data['success'] = True
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def delete_wish_ajax(request):
    response_data = {}
    wish_time_slot_class = request.POST['wish_time_slot']
    wish_time_slot_parsed = wish_time_slot_class.split('y')
    wish_dow = wish_time_slot_parsed[0] + 'y'
    wish_start_time = wish_time_slot_parsed[1]
    wish_start_time = float(wish_start_time.split()[0])
    wish_time_slot = TimeSlot.objects.filter(day_of_week=wish_dow, start_time=wish_start_time)[0]
    # add lecture to user timetable ##########
    user_profile = UserProfile.objects.get(user=request.user)
    user_profile.wish_time_slots.remove(wish_time_slot)
    user_profile.save()
    ##########################################
    response_data['success'] = True
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def get_roomid_ajax(request):
    # request['username']와 자기자신이 들어있는 room을 찾아 그 아이디 반환
    response_data = dict()
    response_data['messages'] = []
    print(request.POST['username'])
    the_other = User.objects.filter(username=request.POST['username'])[0]
    print(the_other)
    chat_list = Chat.objects.all()
    for chat in chat_list:
        if request.user in chat.chatters.all():
            if the_other in chat.chatters.all():
                response_data['id'] = chat.roomid
                for msg in chat.messages.all():
                    response_data['messages'].append([msg.chatter.username, msg.message])
                return HttpResponse(json.dumps(response_data), content_type="application/json")
    new_chat = Chat()
    new_chat.save()
    new_chat.chatters.add(request.user)
    new_chat.chatters.add(the_other)
    new_chat.roomid = str(uuid.uuid4())
    new_chat.save()
    response_data['id'] = new_chat.roomid

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def add_message_ajax(request):
    response_data = {}
    chat_msg = ChatMessage()
    chat_msg.chatter = request.user.username
    chat_msg.message = request.POST['msg']
    chat_msg.save()
    chat = Chat.objects.filter(roomid=request.POST['id'])[0]
    chat.messages.add(chat_msg)
    return HttpResponse(json.dumps(response_data), content_type="application/json")


def notify_ajax(request):
    response_data = {}
    print(request.POST['message'])
    print(request.POST['id'])
    the_other = User.objects.filter(username=request.POST['id'])[0]
    the_other.notifications.create(chatter=request.user.username)
    return HttpResponse(json.dumps(response_data), content_type="application/json")

