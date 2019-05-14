from django.test import TestCase

from pipeline.models import Snapshot


class TestSnapshot(TestCase):
    def test_create_snapshot(self):
        data = {'a': 1, 'b': [1, 2, 3], 'c': {'d': 'd'}}
        snapshot, _ = Snapshot.objects.create_or_get_snapshot(data)
        Snapshot.objects.create_or_get_snapshot(data)
        Snapshot.objects.create_or_get_snapshot(data)
        self.assertEqual(snapshot.data, data)
        self.assertEqual(len(snapshot.md5sum), 32)
        self.assertIsNotNone(snapshot.create_time)
        self.assertEqual(1, Snapshot.objects.filter(md5sum=snapshot.md5sum).count())

    def test_no_change(self):
        data = {'a': 1, 'b': [1, 2, 3], 'c': {'d': 'd'}}
        snapshot, _ = Snapshot.objects.create_or_get_snapshot(data)
        md5, changed = snapshot.has_change(data)
        self.assertFalse(changed)
        self.assertEqual(md5, snapshot.md5sum)
        data = {'a': 2, 'b': [1, 2, 3], 'c': {'d': 'd'}}
        md5, changed = snapshot.has_change(data)
        self.assertTrue(changed)
        self.assertNotEqual(md5, snapshot.md5sum)
