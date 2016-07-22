# -*- coding: utf-8 -*-
from django.apps import AppConfig

from django_stats2 import settings as stats2_settings


class Stats2Config(AppConfig):
    name = 'django_stats2'

    def ready(self):
        assert stats2_settings.USE_CACHE == stats2_settings.DDBB_DIRECT_INSERT == False,\
            "django_stats2: Configuration error. USE_CACHE and "\
            "DDBB_DIRECT_INSERT can't be both False, enable at least one." % stats2_settings.USE_CACHE
