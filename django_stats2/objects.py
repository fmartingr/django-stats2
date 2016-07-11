class Stat(object):
    def __init__(self, *args, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @property
    def object_id(self):
        return self.model_instance.pk
