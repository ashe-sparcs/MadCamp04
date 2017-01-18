from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class TimeSlot(models.Model):
    day_of_week = models.CharField(max_length=10)
    start_time = models.FloatField()  # 10:30 is 10.5
    end_time = models.FloatField()


class Lecture(models.Model):
    lecture_name = models.CharField(max_length=50, default='Any')
    professor_name = models.CharField(max_length=30, default='Undecided')
    time_slots = models.ManyToManyField(TimeSlot)


class ChatMessage(models.Model):
    who = models.CharField(max_length=30)
    what = models.CharField(max_length=100)


class ChatRoom(models.Model):
    messages = models.ManyToManyField(ChatMessage)
    room_id = models.CharField(max_length=40)


class UserProfile(models.Model):
    user = models.OneToOneField(User)
    isAuthenticated = models.BooleanField(default=False)
    # authenticationCode : randomly generated UUID
    authenticationCode = models.CharField(max_length=40)
    taken_lectures = models.ManyToManyField(Lecture)
    wish_time_slots = models.ManyToManyField(TimeSlot)
    chat_rooms = models.ManyToManyField(ChatRoom)



