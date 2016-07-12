django-stats2
=============

Easily create custom stats for your models.

## Usage

TODO

## Contribute

The project provides a sample project to play with the stats2 app, just create a virtualenv, install django and start coding.

```
virtualenv -p python3.5 .virtualenv
source .virtualenv/bin/activate
pip install django
cd sampleproject
```

## Tests

`tox` is used to perform test on different platforms, just install `tox` and run the command.

Keep in mind that this create virtualenv for different python versions, you need to have all the interpreters available to perform the tests on the entire depencency environments.

```
pip install tox
tox
```
