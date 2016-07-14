django-stats2
=============

[![Build Status](https://travis-ci.org/fmartingr/django-stats2.svg?branch=master)](https://travis-ci.org/fmartingr/django-stats2)

Easily create custom stats for your models.

> **NOTE** Development not finished.

# Usage

## Installation

```
pip install git+https://github.com/fmartingr/django-stats2.git#egg=django_stats2
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

## Usage

``` python
from datetime import datetime
from myapp.models import MyModel

obj = MyModel.objects.first()

# Now we can access the Stat using
obj.read_count
obj.read_count.total()  # Same as before
obj.read_count.for_date(date)  # For a current date
obj.read_count.between_date(date_start, date_end)  # Between two dates
obj.read_count.incr(amount=1, date=datetime.now())  # Increment stat by amount
obj.read_count.decr(amount=1, date=datetime.now())  # Decrement stat by amount
obj.read_count.set(amount=1, date=datetime.now())  # Set a fixed amount
obj.read_count.store(date=datetime.now())  # Force store value in database
obj.read_count.flush_cache()  # Removes all cache for stat
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
