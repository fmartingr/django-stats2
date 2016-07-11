# -*- coding: utf-8 -*-

from django.db import models

from django_stats2.models import Stat


class Note(models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField()

    reads = Stat()
    edits = Stat(historical=True)
