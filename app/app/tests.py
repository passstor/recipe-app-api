from django.test import SimpleTestCase

from app.calc import adds, subtract


class CalcTests(SimpleTestCase):
    def test_add_numbers(self):
        self.assertEqual(adds(3, 8), 11)

    def test_subtract(self):
        self.assertEqual(subtract(10, 15), 5)
