from unittest import TestCase

from vfix import find_property, repair_newlines_auto


class TestFindProperty(TestCase):
    def test_simple(self):
        self.assertEqual(find_property('N:Jane;Do;;;'), 1)
        self.assertEqual(find_property('X-EVOLUTION-FILE-AS:Doe, Jane'), 19)
        self.assertEqual(find_property('TEL;TYPE=CELL:+01234567'), 3)
        self.assertEqual(find_property('af43ab32'), -1)
        self.assertEqual(find_property(' af43ab32'), -1)

    def test_escaped_colon(self):
        # should not happen IRL, would be a broken vcard
        self.assertEqual(find_property('TEL\:af43ab32'), -1)


