# -*- coding: utf-8 -*-
from .fields import StatField


class StatsMixin(object):
    """
    Allows a Django model to have some :class:`django_stats2.fields.StatField`
    assigned as attributes.
    """
    def _update_stat_fields(self):
        for key in dir(self):
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
