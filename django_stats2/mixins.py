# -*- coding: utf-8 -*-
from django.contrib.contenttypes.models import ContentType

from .fields import StatField


class StatsMixin:
    def _get_prepare_data(self, model):
        return {
            'content_type': ContentType.objects.get_for_model(model),
            'object_id': model.pk,
        }

    def _update_stat_fields(self):
        for key in dir(self):
            try:
                attr = getattr(self, key)
                if isinstance(attr, StatField):
                    stat = attr.prepare(name=key, model=self, **self._get_prepare_data(self))
                    setattr(self, key, stat)
            except AttributeError:
                # Prevents errors when accesing the managers
                pass

    def __init__(self, *args, **kwargs):
        super(StatsMixin, self).__init__(*args, **kwargs)
        self._update_stat_fields()

    def save(self, *args, **kwargs):
        super(StatsMixin, self).save(*args, **kwargs)
        self._update_stat_fields()
