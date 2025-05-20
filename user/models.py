from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):

    is_borrowing = models.BooleanField(default=False)
    nation_id = models.CharField(max_length=13, blank=True)
    tel = models.CharField(max_length=10,blank=True)
