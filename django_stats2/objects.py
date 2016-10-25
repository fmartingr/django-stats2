# -*- coding: utf-8 -*-
from datetime import datetime

from django.db.models import Sum
from django.contrib.contenttypes.models import ContentType
from django.core.cache import caches
from django.core.cache.backends.base import InvalidCacheBackendError
from django.utils import timezone

from django_stats2.models import ModelStat
from django_stats2 import settings as stats2_settings


class Stat(object):
    cache_key_prefix = stats2_settings.CACHE_PREFIX
    cache_key_format = {
        'history': '{cache_key_prefix}:{prefix}:{name}:{pk}:{date}',
        'total': '{cache_key_prefix}:{prefix}:{name}:{pk}:total',
        'between': '{cache_key_prefix}:{prefix}:{name}:{pk}:{date}_{date_end}',
    }

    def __init__(self, name, model_instance=None):
        """
        Setup the base fields for the stat to work properly and the cache
        connection to store the data.
        """
        self.cache = self._get_cache_instance()
        self.name = name
        self.model_instance = model_instance
        if self.model_instance:
            self.content_type = ContentType.objects.get_for_model(
                self.model_instance)

    # Cache handling
    def _get_cache_instance(self):
        """Returns a django cache object based on the settings configuration"""
        try:
            cache = caches[stats2_settings.CACHE_KEY]
        except InvalidCacheBackendError:
            cache = caches['default']
        return cache

    def _get_stat_prefix(self):
        """
        Return the stat prefix for the cache key
        - Return the lowercase class name for models
        - '_global' otherwise
        """
        if self.model_instance:
            return self.model_instance.__class__.__name__.lower()
        return '_global'

    def _get_cache_key(self, value_type='total', date=None, date_end=None):
        if isinstance(date, datetime):
            date = date.date()

        if isinstance(date_end, datetime):
            date_end = date_end.date()

        return self.cache_key_format.get(value_type).format(
            cache_key_prefix=self.cache_key_prefix,
            prefix=self._get_stat_prefix(),
            name=self.name,
            pk=self.object_id or '',
            date=date,
            date_end=date_end)

    def _get_cache(self, value_type='total', date=None, date_end=None):
        cache_key = self._get_cache_key(value_type, date, date_end)
        return self.cache.get(cache_key)

    def _set_cache(self, value_type='total', date=None, value=0, date_end=None):  # noqa
        cache_key = self._get_cache_key(value_type, date, date_end)
        timeout = getattr(stats2_settings,
                          'CACHE_TIMEOUT_{}'.format(value_type).upper(),
                          None)
        self.cache.set(cache_key, value, timeout=timeout)

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

    def _delete_cache(self, date=None):
        value_type = 'history' if date else 'total'
        cache_key = self._get_cache_key(value_type, date)
        caches[stats2_settings.CACHE_KEY].delete(cache_key)

    # Database handlers
    def _get_manager_kwargs(self, date=None):
        """Returns kwargs to filter ModelStat by Stat type"""
        if self.model_instance:
            manager_kwargs = {
                'content_type_id': self.content_type.pk,
                'object_id': self.object_id,
                'name': self.name
            }
        else:
            manager_kwargs = {
                'name': self.name
            }

        if date:
            manager_kwargs['date'] = date

        return manager_kwargs

    def _get_model_queryset(self, date=timezone.now().date()):
        """Returns the ModelStat queryset for this Stat"""
        manager_kwargs = self._get_manager_kwargs(date)

        model_obj, created = ModelStat.objects.get_or_create(**manager_kwargs)

        return model_obj

    def _get_ddbb(self, value_type='total', date=None):
        if value_type == 'total':
            stat_result = ModelStat.objects.filter(
                **self._get_manager_kwargs()
            ).aggregate(Sum('value'))
            stat = stat_result.get('value__sum')

            return stat or 0

        if value_type == 'history':
            try:
                stat_result = ModelStat.objects.get(
                    **self._get_manager_kwargs(date)
                )
                return stat_result.value
            except ModelStat.DoesNotExist:
                # Assume zero
                pass

        return 0

    def _get_ddbb_between(self, date_start, date_end):
        try:
            stat_result = ModelStat.objects.filter(
                date__gte=date_start,
                date__lte=date_end,
                **self._get_manager_kwargs()
            ).aggregate(Sum('value'))
            stat = stat_result.get('value__sum')
            return stat
        except ModelStat.DoesNotExist:
            # Assume zero
            pass

        return 0

    def _set_ddbb(self, date, value):
        object_kwargs = self._get_manager_kwargs(date)

        try:
            obj = ModelStat.objects.get(**object_kwargs)
        except ModelStat.DoesNotExist:
            obj = ModelStat(**object_kwargs)

        obj.value = value
        obj.save()

    def _incr_ddbb(self, date, value):
        model = self._get_model_queryset(date)
        model.incr(value)

    def _decr_ddbb(self, date, value):
        model = self._get_model_queryset(date)
        model.decr(value)

    # Globals
    def _get_value(self, date=None):
        value_type = 'history' if date else 'total'
        cache_value = self._get_cache(value_type, date)

        # If we don't have a cache value we must retireve it from the ddbb
        if cache_value is None:
            ddbb_value = self._get_ddbb(value_type, date)

            # Store in cache for future access
            self._set_cache(value_type, date, ddbb_value)
            cache_value = ddbb_value

        return cache_value

    def _get_between(self, date_start, date_end):
        cache_value = self._get_cache('between', date_start, date_end)

        # If we don't have the cache value we retrieve it from the ddbb
        if cache_value is None:
            ddbb_value = self._get_ddbb_between(date_start, date_end)

            # Store in cache for future access
            self._set_cache('between', date_start,
                            date_end=date_end, value=ddbb_value)
            cache_value = ddbb_value

        return cache_value

    def _set_value(self, value, date=None):
        value_type = 'history' if date else 'total'

        if stats2_settings.USE_CACHE:
            self._set_cache(value_type=value_type, date=date, value=value)

        if stats2_settings.DDBB_DIRECT_INSERT:
            self._set_ddbb(date=date, value=value)

        # Delete cache for this totals if a specified date is modified
        # and database direct insert is present
        if date and stats2_settings.DDBB_DIRECT_INSERT:
            self._delete_cache()

        return value

    # Public
    def get(self, date=None):
        return int(self._get_value(date=date))

    def get_for_date(self, date):
        return self.get(date)

    def get_between_date(self, date_start, date_end):
        assert date_start < date_end, "Start date must be before end date."
        return self._get_between(date_start, date_end)

    def total(self):
        return int(self._get_value())

    def set(self, value, date=datetime.today()):
        return self._set_value(value, date)

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

    def store(self, value, date=datetime.now().date()):
        return self._set_ddbb(date, value)

    @property
    def object_id(self):
        """
        :returns: Model instance primary key
        :rtype: int
        """
        if self.model_instance:
            return self.model_instance.pk
        return None

    def __repr__(self):
        return str(self.total())

    def __int__(self):
        return self.total()
