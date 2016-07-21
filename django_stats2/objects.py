# -*- coding: utf-8 -*-
from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django.utils import timezone

from django_stats2.models import ModelStat
from django_stats2 import settings as stats2_settings


class Stat(object):
    cache_key_prefix = 'stats2'
    cache_key_format = {
        'history': '{cache_key_prefix}:{prefix}:{name}:{pk}:{date}:history',
        'total': '{cache_key_prefix}:{prefix}:{name}:{pk}:total',
    }

    def __init__(self, name, model_instance):
        """
        Setup the base fields for the stat to work properly and the cache
        connection to store the data.
        """
        self.cache = self._get_cache_instance()
        self.name = name
        self.model_instance = model_instance
        self.content_type = ContentType.objects.get_for_model(
            self.model_instance)

    # Cache handling
    def _get_cache_instance(self):
        """Returns a django cache object based on the settings configuration"""
        try:
            cache = caches['stats2']
        except InvalidCacheBackendError:
            cache = caches['default']
        # TODO handle unconfigured caches
        return cache

    def _get_cache_key(self, value_type='total', date=None):
        return self.cache_key_format.get(value_type).format(
            cache_key_prefix=self.cache_key_prefix,
            prefix=self.model_instance.__class__.__name__.lower(),
            name=self.name,
            pk=self.object_id,
            date=date
        )

    def _get_cache(self, value_type='total', date=None):
        cache_key = self._get_cache_key(value_type, date)
        return self.cache.get(cache_key)

    def _set_cache(self, value_type='total', date=None, value=0):
        cache_key = self._get_cache_key(value_type, date)
        self.cache.set(cache_key, value)
        return value

    def _incr_cache(self, date, value):
        cache_key_history = self._get_cache_key('history', date)
        cache_key_total = self._get_cache_key('total', date)
        try:
            self.cache.incr(cache_key_history, value)
        except ValueError:
            self._set_cache('history', date, value)

        try:
            self.cache.incr(cache_key_total, value)
        except ValueError:
            # Will get cached on get()
            pass

    def _decr_cache(self, date, value):
        cache_key_history = self._get_cache_key('history', date)
        cache_key_total = self._get_cache_key('total', date)

        try:
            self.cache.decr(cache_key_history, value)
        except ValueError:
            self._set_cache('history', date, value)

        try:
            self.cache.decr(cache_key_total, value)
        except ValueError:
            # Will get cached on get()
            pass

    # Database handlers
    def _get_model_queryset(self, date=timezone.now().date()):
        model_obj, created = ModelStat.objects.get_or_create(
            content_type_id=self.content_type.pk,
            object_id=self.object_id,
            date=date,
            name=self.name
        )

        return model_obj

    def _get_ddbb(self, value_type='total', date=None):
        if value_type == 'total':
            stat_result = ModelStat.objects.filter(
                content_type_id=self.content_type.pk,
                object_id=self.object_id,
                name=self.name,
            ).aggregate(Sum('value'))
            stat = stat_result.get('value_sum')

        return stat or 0

    def _incr_ddbb(self, date, value):
        model = self._get_model_queryset(date)
        model.incr(value)

    def _decr_ddbb(self, date, value):
        model = self._get_model_queryset(date)
        model.decr(value)

    # Globals
    def _get_value(self, value_type='total', date=None):
        cache_value = self._get_cache(value_type, date)

        # If we don't have a cache value we must retireve it from the ddbb
        if cache_value is None:
            ddbb_value = self._get_ddbb(value_type, date)
            # Store in cache for future access
            cache_value = self._set_cache(
                value_type, date, ddbb_value)

        return cache_value

    # Public
    def get(self):
        return int(self._get_value())

    def incr(self, value=1, date=timezone.now().date()):
        if stats2_settings.USE_CACHE:
            self._incr_cache(date, value)
        if stats2_settings.DDBB_DIRECT_INSERT:
            self._incr_ddbb(date, value)

    def decr(self, value=1, date=timezone.now().date()):
        if stats2_settings.USE_CACHE:
            self._decr_cache(date, value)
        if stats2_settings.DDBB_DIRECT_INSERT:
            self._decr_ddbb(date, value)

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
