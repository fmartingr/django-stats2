# -*- coding: utf-8 -*-
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError

from django_stats2.models import ModelStat


class Stat(object):
    cache_key_format = {
        'history': '{prefix}:{name}:{pk}:{date}:history',
        'total': '{prefix}:{name}:{pk}:total',
    }

    def __init__(self, name, model_instance):
        """
        Setup the base fields for the stat to work properly and the cache
        connection to store the data.
        """
        self.cache = self._get_cache()
        self.name = name
        self.model_instance = model_instance
        self.content_type = ContentType.objects.get_for_model(
            self.model_instance)

    # Cache handling
    def _get_cache(self):
        """Returns a django cache object based on the settings configuration."""
        try:
            cache = caches['stats2']
        except InvalidCacheBackendError:
            cache = caches['default']
        return cache

    def _get_cache_key(self, value_type='total', date=None):
        return self.cache_key_format.get(value_type).format(
            prefix=self.model_instance.__class__.__name__.lower(),
            name=self.name,
            pk=self.object_id,
            date=date
        )

    def _get_value_from_cache(self, value_type='total', date=None):
        cache_key = self._get_cache_key(value_type, date)
        return self.cache.get(cache_key)

    def _set_value_for_cache(self, value_type='total', date=None, value=0):
        cache_key = self._get_cache_key(value_type, date)
        self.cache.set(cache_key, value)
        return value

    # Database handlers
    def _get_value_from_ddbb(self, value_type='total', date=None):
        if value_type == 'total':
            stat_result = ModelStat.objects.filter(
                content_type=self.content_type,
                object_id=self.object_id,
                name=self.name,
            ).aggregate(Sum('value'))
            stat = stat_result.get('value_sum')

        return stat or 0

    def _get_value(self, value_type='total', date=None):
        cache_value = self._get_value_from_cache(value_type, date)

        # If we don't have a cache value we must retireve it from the ddbb
        if cache_value is None:
            ddbb_value = self._get_value_from_ddbb(value_type, date)
            # Store in cache for future access
            cache_value = self._set_value_for_cache(value_type, date, ddbb_value)

        return cache_value

    # Globals
    def get(self):
        return int(self._get_value())

    @property
    def object_id(self):
        """
        :returns: Model instance primary key
        :rtype: int
        """
        return self.model_instance.pk

    def __repr__(self):
        return str(self._get_value())

    def __int__(self):
        return self._get_value()
