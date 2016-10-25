# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ModelStat(models.Model):
    content_type = models.ForeignKey(ContentType,
                                     on_delete=models.CASCADE,
                                     null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    date = models.DateField(db_index=True)
    name = models.CharField(max_length=128)
    value = models.IntegerField(default=0)

    class Meta:
        unique_together = (
            ('content_type', 'object_id', 'name', 'date'),
        )
        index_together = (
            ('content_type', 'object_id'),
        )

    def incr(self, value):
        self.value += value
        self.save()

    def decr(self, value):
        self.value -= value
        self.save()
