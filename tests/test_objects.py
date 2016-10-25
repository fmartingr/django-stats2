import datetime
from unittest import TestCase

from django.core.cache import caches
from django.test.testcases import TransactionTestCase

from django_stats2 import settings as stats2_settings
from django_stats2.objects import Stat
from django_stats2.models import ModelStat

from .models import Note


class StatTestCase(TestCase):
    def setUp(self):
        self.stat = Stat(name='total_visits')
        self.note = Note.objects.create(title='Title', content='Content')

    def test_stat_prefix_is_correct(self):
        self.assertEqual(self.stat._get_stat_prefix(), '_global')
        self.assertEqual(self.note.reads._get_stat_prefix(), 'note')


class ModelStatTotalsTestCase(TestCase):
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


class ModelStatCacheTestCase(TransactionTestCase):
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


class StatOperationsBase:
    def test_incr(self):
        stat = self.stat.get()

        self.stat.incr()
        self.assertEquals(stat+1, self.stat.get())

        self.stat.incr(2)
        self.assertEquals(stat+3, self.stat.get())

        self.assertEquals(ModelStat.objects.first().value, 3)

    def test_incr_date(self):
        self.stat.incr()
        self.stat.incr(
            date=datetime.datetime.now()+datetime.timedelta(days=-1))
        self.assertEquals(ModelStat.objects.count(), 2)

    def test_decr(self):
        stat = self.stat.get()

        self.stat.decr()
        self.assertEquals(stat-1, self.stat.get())

        self.stat.decr(2)
        self.assertEquals(stat-3, self.stat.get())

        self.assertEquals(ModelStat.objects.first().value, -3)

    def test_decr_date(self):
        self.stat.decr()
        self.stat.decr(
            date=datetime.datetime.now()+datetime.timedelta(days=-1))

        self.assertEquals(ModelStat.objects.count(), 2)

    def test_set(self):
        with self.assertNumQueries(self.queries_per_set):
            self.stat.set(10)

        self.assertEqual(
            caches[stats2_settings.CACHE_KEY].get(
                self.stat._get_cache_key('history',
                                               datetime.date.today())),
            10)

    def test_set_date(self):
        yesterday = datetime.datetime.utcnow()+datetime.timedelta(days=-1)
        today = datetime.datetime.utcnow()

        self.stat.set(10, date=yesterday)
        self.assertEqual(self.stat.get(), 10)
        self.assertEqual(self.stat.get(date=today), 0)
        self.assertEqual(
            caches[stats2_settings.CACHE_KEY].get(self.stat._get_cache_key(date=today)),
            10)

    def test_get_total(self):
        yesterday = datetime.date.today()+datetime.timedelta(days=-1)
        yesterday2 = datetime.date.today()+datetime.timedelta(days=-2)
        yesterday3 = datetime.date.today()+datetime.timedelta(days=-3)

        with self.assertNumQueries(self.queries_per_set*3):
            self.stat.set(date=yesterday, value=1)
            self.stat.set(date=yesterday2, value=2)
            self.stat.set(date=yesterday3, value=3)

        self.assertIn(
            self.stat._get_cache_key(value_type='history',
                                           date=yesterday),
            caches[stats2_settings.CACHE_KEY])
        self.assertIn(
            self.stat._get_cache_key(value_type='history',
                                           date=yesterday2),
            caches[stats2_settings.CACHE_KEY])
        self.assertIn(
            self.stat._get_cache_key(value_type='history',
                                           date=yesterday3),
            caches[stats2_settings.CACHE_KEY])

        with self.assertNumQueries(1):
            self.assertEqual(self.stat.total(), 6)

    def test_get_date(self):
        yesterday = datetime.date.today()+datetime.timedelta(days=-1)
        self.stat.set(10, date=yesterday)

        with self.assertNumQueries(0):
            self.assertEquals(
                self.stat.get_for_date(yesterday),
                10)

        # Clear cache and try again to try get from ddbb
        caches[stats2_settings.CACHE_KEY].clear()

        with self.assertNumQueries(1):
            self.assertEquals(
                self.stat.get_for_date(yesterday),
                10)

    def test_get_between(self):
        # Fill the past 5 days
        for i in range(1, 6):
            day = datetime.date.today() + datetime.timedelta(days=i*-1)
            self.stat.set(date=day, value=1)

        with self.assertNumQueries(1):
            two_days = self.stat.get_between_date(
                datetime.date.today() + datetime.timedelta(days=-2),
                datetime.date.today() + datetime.timedelta(days=-1)
            )

        # Test cache
        with self.assertNumQueries(0):
            two_days = self.stat.get_between_date(
                datetime.date.today() + datetime.timedelta(days=-2),
                datetime.date.today() + datetime.timedelta(days=-1)
            )

        # Assert result
        self.assertEqual(two_days, 2)

        four_days = self.stat.get_between_date(
            datetime.date.today() + datetime.timedelta(days=-4),
            datetime.date.today() + datetime.timedelta(days=-1)
        )
        self.assertEqual(four_days, 4)

    def test_store(self):
        day = datetime.date.today()
        self.stat.store(3, date=day)

        with self.assertNumQueries(1):
            self.assertEquals(self.stat.get(date=day), 3)


class ModelStatOperationsTestCase(StatOperationsBase, TransactionTestCase):
    queries_per_set = 3

    def setUp(self):
        self.note = Note.objects.create(title='Title', content='Content')
        self.stat = self.note.reads

    def tearDown(self):
        self.note.delete()
        ModelStat.objects.all().delete()
        caches[stats2_settings.CACHE_KEY].clear()


class GlobalStatOperationsTestCase(StatOperationsBase, TransactionTestCase):
    queries_per_set = 3

    def setUp(self):
        self.stat = Stat(name='total_visits')

    def tearDown(self):
        ModelStat.objects.all().delete()
        caches[stats2_settings.CACHE_KEY].clear()
