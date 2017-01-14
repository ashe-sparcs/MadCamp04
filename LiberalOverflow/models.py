from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User)
    isAuthenticated = models.BooleanField(default=False)
    # authenticationCode : randomly generated UUID
    authenticationCode = models.CharField(max_length=40)
