from django.shortcuts import render
from django.core.mail import send_mail
# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText
import base64


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
    return {'raw': base64.urlsafe_b64encode(message.as_string())}


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
        message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
        print('Message Id: ' + message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: ' + error)


# Create your views here.
def home(request):
    return render(request, 'home.html')


def register(request):
    return render(request, 'register.html')


def register_complete(request):
    # 인증 메일 보내기
    print(request.POST.get('email'))
    send_mail(
        'LiberalOverflow Authentication email',
        'Here is the message.',
        'master.liberaloverflow@gmail.com',
        [request.POST.get('email')],
        fail_silently=False,
    )
    # 완료 페이지 띄우기
    return render(request, 'register_complete.html')
