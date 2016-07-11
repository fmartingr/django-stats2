# -*- coding: utf-8 -*-

from django_stats2.objects import Stat


class StatField(object):
    name = None
    content_type = None
    object_id = None

    def __init__(self, historical=False):
        self.historical = True
        self.name = None
        self.content_type = None
        self.object_id = None

    def prepare(self, name, model, content_type=1, object_id=1):
        self.name = name
        self.content_type = content_type
        self.object_id = object_id
        self.model = model

        return Stat(
            model_instance=self.model,
            name=self.name,
            content_type=self.content_type,
        )
