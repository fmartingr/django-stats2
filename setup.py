import re
import sys
import os
from distutils.core import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search(
        "^__version__ = ['\"]([^'\"]+)['\"]",
        init_py, re.MULTILINE).group(1)


REPO = 'https://github.com/fmartingr/django-stats2'
VERSION = get_version('django_stats2')

if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    args = {'version': VERSION}
    print("You probably want to also tag the version now:")
    print("  git tag -a %(version)s -m 'version %(version)s'" % args)
    print("  git push --tags")
    sys.exit()


setup(
    name='django_stats2',
    packages=[
        'django_stats2',
        'django_stats2/migrations',
    ],
    version=VERSION,
    description='Easily create stats for your models',
    author='Felipe Martin',
    author_email='me@fmartingr.com',
    url=REPO,
    download_url='{}/tarball/{}'.format(REPO, VERSION),
    keywords=['django', 'stats', ],
    classifiers=[],
)
