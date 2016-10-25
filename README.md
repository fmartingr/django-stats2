django-stats2
=============

[![Build Status](https://travis-ci.org/fmartingr/django-stats2.svg?branch=master)](https://travis-ci.org/fmartingr/django-stats2)

Easily create custom stats for your models.

# Usage

## Installation

```
pip install django_stats2
```

## Configuration


### Model stats
``` python
# models.py
from django.db import models

from django_stats2.mixins import StatsMixin
from django_stats2.fields import StatField


class MyModel(StatsMixin, models.Model):
     # ... your fields here

     read_count = StatField()
```

### Global stats

``` python
from django_stats2.objects import Stat

stat = Stat(name='total_visits')
```

## Settings
``` python
# Prefix for the cache keys
STATS2_CACHE_PREFIX = 'stats2'

# Cache key from settings.CACHES
STATS2_CACHE_KEY = 'default'

# Cache-Database interaction
# Can't be the same setting, if cache is disabled, database direct
# insert should be enabled (otherwise your stats would't be stored!)
STATS2_USE_CACHE = True

STATS2_DDBB_DIRECT_INSERT = False

# Cache timeouts for the key types
# Cache timeout for the totals
STATS2_CACHE_TIMEOUT_TOTAL = None

# Cache timeout for a certain date
STATS2_CACHE_TIMEOUT_HISTORY = None

# Cache timeout for between dates
STATS2_CACHE_TIMEOUT_BETWEEN = 60*60*24

```

> **NOTE ON CACHES:** While stats2 does it's own cache removal, the `between` cache key can't be invalidated due to the app architecture and django limitations, so keep in mind that if the `CACHE_TIMEOUT_BETWEEN` is `None` those keys will **never be invalidated**.

## Usage

``` python
from datetime import date
from myapp.models import MyModel

obj = MyModel.objects.first()

stat = obj.read_count
# or
stat = Stat(name='total_visits')

# Now we can access the Stat using
stat # Returns str(stat)
stat.get([date]) # Returns int stat, returns total if date not present
stat.total()  # Same as before but returns int
stat.get_for_date(date)  # Return stat for a current date (same as .get(date))
stat.get_between_date(date_start, date_end)  # Between two dates
stat.incr(value=1, date=date.today())  # Increment stat by amount
stat.decr(value=1, date=date.today())  # Decrement stat by amount
stat.set(value=1, date=date.today())  # Set a fixed amount
stat.store(value=1, date=date.today())  # Force store value in database
```

# Contribute

The project provides a sample project to play with the stats2 app, just create a virtualenv, install django and start coding.

```
python3 -m venv .virtualenv
source .virtualenv/bin/activate
pip install django
cd sampleproject
```

# Tests

`tox` is used to perform test on different platforms, just install `tox` and run the command.

Keep in mind that this create virtualenv for different python versions, you need to have all the interpreters available to perform the tests on the entire depencency environments.

```
pip install tox
tox
```
