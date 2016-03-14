from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Dropbox(models.Model):
    """Dropbox model

    Include access token dropbox key

    Extends:
        django.contrib.auth.models.Model

    Variables:
        user {one to one field} -- Users model
        access_token {charfield} -- access token
    """
    user = models.OneToOneField(User)
    access_token = models.CharField(max_length=40)
