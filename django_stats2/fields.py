# -*- coding: utf-8 -*-


class Stat(object):
    name = None
    content_type = None
    object_id = None

    def __init__(self, historical=False):
        self.historical = True

    def prepare(self, name, model, content_type=1, object_id=1):
        self.name = name
        self.content_type = content_type
        self.object_id = object_id
        self.model = model
