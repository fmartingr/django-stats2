# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType


class Stat(object):
    def __init__(self, historical, name, model_instance):
        """ Setup the base fields for the stat to work properly """
        self.name = name
        self.model_instance = model_instance
        self.historical = historical
        self.content_type = ContentType.objects.get_for_model(
            self.model_instance)

    @property
    def object_id(self):
        """
        :returns: Model instance primary key
        :rtype: int
        """
        return self.model_instance.pk
