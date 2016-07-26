# -*- coding: utf-8 -*-
from django.conf import settings


# Prefix for the cache keys
CACHE_PREFIX = getattr(settings, 'STATS2_CACHE_PREFIX', 'stats2')

# Cache key from settings.CACHES
CACHE_KEY = getattr(settings, 'STATS2_CACHE_KEY', 'default')

# Cache-Database interaction
# Can't be the same setting, if cache is disabled, database direct
# insert should be enabled (otherwise your stats would't be stored!)
USE_CACHE = getattr(settings, 'STATS2_USE_CACHE', True)

DDBB_DIRECT_INSERT = getattr(settings,
                             'STATS2_DDBB_DIRECT_INSERT',
                             not USE_CACHE)

# Cache timeouts for the key types

# Cache timeout for the totals
CACHE_TIMEOUT_TOTAL = getattr(settings,
                              'STATS2_CACHE_TIMEOUT_TOTAL',
                              None)

# Cache timeout for a certain date
CACHE_TIMEOUT_HISTORY = getattr(settings,
                                'STATS2_CACHE_TIMEOUT_HISTORY',
                                None)

# Cache timeout for between dates
CACHE_TIMEOUT_BETWEEN = getattr(settings,
                                'STATS2_CACHE_TIMEOUT_BETWEEN',
                                60*60*24)
