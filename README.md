django-stats2
=============

[![Build Status](https://travis-ci.org/fmartingr/django-stats2.svg?branch=master)](https://travis-ci.org/fmartingr/django-stats2)

Easily create custom stats for your models.

> **NOTE** Development not finished.

# Usage

## Installation

```
pip install django_stats2
```

## Configuration

``` python
# models.py
from django.db import models

from django_stats2.mixins import StatsMixin
from django_stats2.fields import StatField


class MyModel(StatsMixin, models.Model):
     # ... your fields here

     read_count = StatField()
```

## Settings
``` python
# Prefix for the cache keys
CACHE_PREFIX = 'stats2'

# Cache key from settings.CACHES
CACHE_KEY = 'default'

# Cache-Database interaction
# Can't be the same setting, if cache is disabled, database direct
# insert should be enabled (otherwise your stats would't be stored!)
USE_CACHE = True

DDBB_DIRECT_INSERT = False

# Cache timeouts for the key types
# Cache timeout for the totals
CACHE_TIMEOUT_TOTAL = None

# Cache timeout for a certain date
CACHE_TIMEOUT_HISTORY = None

# Cache timeout for between dates
CACHE_TIMEOUT_BETWEEN = 60*60*24

```

> **NOTE ON CACHES:** While stats2 does it's own cache removal, the `between` cache key can't be invalidated due to the app architecture and django limitations, so keep in mind that if the `CACHE_TIMEOUT_BETWEEN` is `None` those keys will **never be invalidated**.

## Usage

``` python
from datetime import date
from myapp.models import MyModel

obj = MyModel.objects.first()

# Now we can access the Stat using
obj.read_count # Returns str(stat)
obj.read_count.get([date]) # Returns int stat, returns total if date not present
obj.read_count.total()  # Same as before but returns int
obj.read_count.get_for_date(date)  # Return stat for a current date (same as .get(date))
obj.read_count.get_between_date(date_start, date_end)  # Between two dates
obj.read_count.incr(value=1, date=date.today())  # Increment stat by amount
obj.read_count.decr(value=1, date=date.today())  # Decrement stat by amount
obj.read_count.set(value=1, date=date.today())  # Set a fixed amount
obj.read_count.store(value=1, date=date.today())  # Force store value in database
```

# Contribute

The project provides a sample project to play with the stats2 app, just create a virtualenv, install django and start coding.

```
virtualenv -p python3.5 .virtualenv
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
