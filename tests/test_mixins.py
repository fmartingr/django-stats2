from unittest import TestCase

from .models import Note

from django.contrib.contenttypes.models import ContentType

from django_stats2.objects import Stat


class MixinTestCase(TestCase):
    stat_name1 = 'reads'

    def setUp(self):
        self.note = Note()

    def tearDown(self):
        if self.note.pk:
            self.note.delete()

    def test_mixin_setup_stat_with_model_info(self):
        """
        Check that StatsMixin setup the required fields for the Stat object
        to work with the ModelStat model.
        """
        attr = getattr(self.note, self.stat_name1)

        content_type = ContentType.objects.get_for_model(Note)

        self.assertTrue(isinstance(attr, Stat))
        self.assertEquals(attr.content_type.pk, content_type.pk)
        self.assertEquals(attr.object_id, self.note.pk)
        self.assertEquals(attr.name, self.stat_name1)

    def test_mixin_setup_fills_pk(self):
        self.note = Note.objects.create(title='Test', content='Content')

        attr = getattr(self.note, self.stat_name1)

        self.assertTrue(attr.object_id, self.note.pk)

    def test_mixin_setup_when_saved_after_creation(self):
        self.note = Note()
        attr = getattr(self.note, self.stat_name1)

        self.assertIsNone(attr.object_id)

        self.note.tilte = 'Test'
        self.note.content = 'Test'
        self.note.save()

        self.assertEquals(attr.object_id, self.note.pk)

    def test_mixin_stat_dont_screw_up_between_instances(self):
        note1 = Note.objects.create(title='1', content='1')
        note2 = Note.objects.create(title='2', content='2')

        # Check that the instance is different
        self.assertNotEqual(id(getattr(note1, self.stat_name1)),
                            id(getattr(note2, self.stat_name1)))
