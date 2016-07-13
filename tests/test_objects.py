import datetime
from unittest import TestCase

from django.core.cache import caches
from django.test.testcases import TransactionTestCase

from django_stats2.models import ModelStat

from .models import Note


class StatTotalsTestCase(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title='Title', content='content')

    def tearDown(self):
        self.note.delete()
        ModelStat.objects.all().delete()
        caches['default'].clear()

    def test_stat_returns_zero_and_dont_create_modelstat_when_no_data(self):
        """
        Getting totals from a stat that don't have any should return zero and
        do not create a ModelStat object.
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


class StatOperationsTestCase(TransactionTestCase):
    def setUp(self):
        self.note = Note.objects.create(title='Title', content='Content')

    def tearDown(self):
        self.note.delete()
        ModelStat.objects.all().delete()
        caches['default'].clear()

    def test_incr(self):
        stat = self.note.reads.get()

        self.note.reads.incr()
        self.assertEquals(stat+1, self.note.reads.get())

        self.note.reads.incr(2)
        self.assertEquals(stat+3, self.note.reads.get())

        self.assertEquals(ModelStat.objects.first().value, 3)

    def test_incr_date(self):
        self.note.reads.incr()
        self.note.reads.incr(
            date=datetime.datetime.now()+datetime.timedelta(days=-1))
        self.assertEquals(ModelStat.objects.count(), 2)

    def test_decr(self):
        stat = self.note.reads.get()

        self.note.reads.decr()
        self.assertEquals(stat-1, self.note.reads.get())

        self.note.reads.decr(2)
        self.assertEquals(stat-3, self.note.reads.get())

        self.assertEquals(ModelStat.objects.first().value, -3)

    def test_decr_date(self):
        self.note.reads.decr()
        self.note.reads.decr(
            date=datetime.datetime.now()+datetime.timedelta(days=-1))
        self.assertEquals(ModelStat.objects.count(), 2)

    # def test_set(self):
    #     pass

    # def test_set_date(self):
    #     pass

    # def test_get(self):
    #     pass

    # def test_get_date(self):
    #     pass

    # def test_get_between(self):
    #     pass
