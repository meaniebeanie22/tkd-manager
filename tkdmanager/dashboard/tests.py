from django.test import TestCase
from dashboard.models import Belt
from django.core.exceptions import ValidationError


class BeltTestCase(TestCase):
    def setUp(self):
        Belt.objects.create(degree=1, name="White")

    def test_refuse_duplicate_degree_belts(self):
        """Can't have two belts in the same style with the same degree"""
        with self.assertRaises(ValidationError):
            Belt.objects.create(degree=1, name="Bad White Belt!")
