# -*- coding: utf-8 -*-

from django.db import models

from django_stats2.mixins import StatsMixin
from django_stats2.fields import StatField


class Note(StatsMixin, models.Model):
    title = models.CharField(max_length=128)
    content = models.TextField()

    reads = StatField()
    edits = StatField()
