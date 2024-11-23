from django.db import models
import datetime
from django.utils import timezone


class UserField(models.Model):
    username = models.CharField(max_length=200)
    date = models.DateTimeField("enter time")

    def __str__(self):
        return self.user_text
