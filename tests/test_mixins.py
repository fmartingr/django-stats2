from unittest import TestCase

from .models import Note

from django.contrib.contenttypes.models import ContentType

from django_stats2.fields import Stat


class MixinTestCase(TestCase):
    stat_name = 'reads'

    def test_mixin_setup_stat_with_model_info(self):
        """
        Check that StatsMixin setup the required fields for the Stat object
        to work with the ModelStat model.
        """
        note = Note()

        attr = getattr(note, self.stat_name)

        content_type = ContentType.objects.get_for_model(Note)

        self.assertTrue(isinstance(attr, Stat))
        self.assertEquals(attr.content_type.pk, content_type.pk)
        self.assertEquals(attr.object_id, note.pk)
        self.assertEquals(attr.model, note)
        self.assertEquals(attr.name, self.stat_name)

    def test_mixin_setup_fills_pk(self):
        note = Note.objects.create(title='Test', content='Content')

        attr = getattr(note, self.stat_name)

        self.assertTrue(attr.object_id, note.pk)

    def test_mixin_setup_when_saved_after_creation(self):
        note = Note()
        attr = getattr(note, self.stat_name)

        self.assertIsNone(attr.object_id)

        note.tilte = 'Test'
        note.content = 'Test'
        note.save()

        self.assertEquals(attr.object_id, note.pk)

    def test_mixin_stat_dont_screw_up_between_instances(self):
        note1 = Note.objects.create(title='1', content='1')
        note2 = Note.objects.create(title='2', content='2')

        self.assertNotEqual(getattr(note1, self.stat_name).object_id,
                            getattr(note2, self.stat_name).object_id)
