# -*- coding: utf-8 -*-
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class ModelStat(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    date = models.DateField(null=True, db_index=True)
    name = models.CharField(max_length=128)
    value = models.IntegerField()

    class Meta:
        index_together = (
            ('content_type', 'object_id'),
        )
