from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Dropbox(models.Model):
    user = models.OneToOneField(User)
    access_token = models.CharField(max_length=40)
