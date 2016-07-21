# -*- coding: utf-8 -*-
from django.conf import settings


USE_CACHE = getattr(settings, 'STATS2_USE_CACHE', True)
DDBB_DIRECT_INSERT = getattr(settings,
                             'STATS2_DDBB_DIRECT_INSERT',
                             not USE_CACHE)
