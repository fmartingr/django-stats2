# -*- coding: utf-8 -*-
from django_stats2.objects import Stat


class StatField(object):
    """
    The main field object to use with django models that works with
    :class:`django_stats2.mixins.StatsMixin` to create the appropiate
    :class:`django_stats2.objects.Stat` instances for every field in the model.
    """
    def prepare(self, name, model_instance):
        """
        Creates a new :class:`django_stats2.objects.Stat`.

        :param name: The name of the stat
        :type name: string
        :param model: The model instance to assign this stat to
        :type model: :class:`django.db.models.Model`
        :rtype: :class:`django_stats2.objects.Stat`
        """
        return Stat(
            name=name,
            model_instance=model_instance,
        )
