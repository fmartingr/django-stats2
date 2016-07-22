import datetime
from unittest import TestCase

from django.core.cache import caches
from django.test.testcases import TransactionTestCase

from django_stats2 import settings as stats2_settings
from django_stats2.models import ModelStat

from .models import Note


class StatTotalsTestCase(TestCase):
    def setUp(self):
        self.note = Note.objects.create(title='Title', content='content')

    def tearDown(self):
        self.note.delete()
        ModelStat.objects.all().delete()
        caches[stats2_settings.CACHE_KEY].clear()

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
        caches[stats2_settings.CACHE_KEY].clear()

    def test_retrieve_stat_create_cache(self):
        value = self.note.reads.get()

        self.assertEquals(
            caches[stats2_settings.CACHE_KEY].get(self.note.reads._get_cache_key()),
            value
        )

    def test_retireve_stat_second_time_uses_cache_instead_of_query(self):
        with self.assertNumQueries(1):
            stat = self.note.reads.get()

        with self.assertNumQueries(0):
            stat2 = self.note.reads.get()

        self.assertEquals(stat, stat2)


class StatOperationsBaseTestCase(TransactionTestCase):
    def setUp(self):
        self.note = Note.objects.create(title='Title', content='Content')

    def tearDown(self):
        self.note.delete()
        ModelStat.objects.all().delete()
        caches[stats2_settings.CACHE_KEY].clear()

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

    def test_set(self):
        self.note.reads.set(10)
        self.assertEqual(
            caches[stats2_settings.CACHE_KEY].get(self.note.reads._get_cache_key()),
            10)

    def test_set_date(self):
        yesterday = datetime.datetime.utcnow()+datetime.timedelta(days=-1)
        today = datetime.datetime.utcnow()

        self.note.reads.set(10, date=yesterday)
        self.assertEqual(self.note.reads.get(), 10)
        self.assertEqual(self.note.reads.get(date=today), 0)
        self.assertEqual(
            caches[stats2_settings.CACHE_KEY].get(self.note.reads._get_cache_key(date=today)),
            10)

    def test_get_total(self):
        yesterday = datetime.datetime.utcnow()+datetime.timedelta(days=-1)
        yesterday2 = datetime.datetime.utcnow()+datetime.timedelta(days=-2)
        yesterday3 = datetime.datetime.utcnow()+datetime.timedelta(days=-3)

        with self.assertNumQueries(3*3):
            self.note.reads.set(date=yesterday, value=1)
            self.note.reads.set(date=yesterday2, value=2)
            self.note.reads.set(date=yesterday3, value=3)

        for d in (yesterday, yesterday2, yesterday3):
            self.assertTrue(
                self.note.reads._get_cache_key(date=d) in caches[stats2_settings.CACHE_KEY]
            )

        # self.assertEqual(self.note.reads.total(), 6)

    # def test_get(self):
    #     pass

    # def test_get_date(self):
    #     pass

    # def test_get_between(self):
    #     pass
