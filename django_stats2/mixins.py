# -*- coding: utf-8 -*-
from .fields import StatField


class StatsMixin(object):
    """
    Allows a Django model to have some :class:`django_stats2.fields.StatField`
    assigned as attributes.
    """
    def _get_stat_fields(self):
        stat_fields = []
        model = type(self)
        for key, value in model.__dict__.items():
            if isinstance(value, StatField):
                stat_fields.append(key)
        return stat_fields

    def _update_stat_fields(self):
        for key in self._get_stat_fields():
            try:
                attr = getattr(self, key)
                if isinstance(attr, StatField):
                    stat = attr.prepare(name=key, model_instance=self)
                    setattr(self, key, stat)
            except AttributeError:
                # Prevents errors when accesing the managers
                pass

    def __init__(self, *args, **kwargs):
        """Update the stat fields on model initialization"""
        super(StatsMixin, self).__init__(*args, **kwargs)
        self._update_stat_fields()

    def save(self, *args, **kwargs):
        """Update the stat fields on model saving (handle creation)"""
        super(StatsMixin, self).save(*args, **kwargs)
        self._update_stat_fields()
