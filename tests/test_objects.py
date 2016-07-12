from unittest import TestCase

from django.core.cache import caches
from django.test.testcases import TransactionTestCase

from django_stats2.models import ModelStat

from .models import Note


class StatTestCase(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title='Title', content='content')

    def tearDown(self):
        self.note.delete()
        ModelStat.objects.all().delete()
        caches['default'].clear()

    def test_stat_returns_zero_and_dont_create_modelstat_when_nonexistant_totals(self):
        """
        Getting totals from a stat that don't have any should return zero and do not
        create a ModelStat object.
        """
        self.assertEquals(self.note.reads.get(), 0)
        self.assertEquals(ModelStat.objects.count(), 0)


class StatCacheTestCase(TransactionTestCase):
    def setUp(self):
        self.note = Note.objects.create(title='Title', content='Content')

    def tearDown(self):
        self.note.delete()
        ModelStat.objects.all().delete()
        caches['default'].clear()

    def test_retrieve_stat_create_cache(self):
        value = self.note.reads.get()

        self.assertEquals(
            caches['default'].get(self.note.reads._get_cache_key()),
            value
        )

    def test_retireve_stat_second_time_uses_cache_instead_of_query(self):
        with self.assertNumQueries(1):
            stat = self.note.reads.get()

        with self.assertNumQueries(0):
            stat2 = self.note.reads.get()

        self.assertEquals(stat, stat2)
