import unittest
from datetime import  datetime
from src.dataStructures.MasonTimeUtils import get_utc_datetime_from_iso8601_string

class MyTestCase(unittest.TestCase):
    def test_basic_utc_string(self):
        iso_string="2020-11-12T13:14:15Z"
        dt=get_utc_datetime_from_iso8601_string(iso_string)
        #dt=datetime()

        self.assertEqual(dt.hour, 13)
        self.assertEqual(dt.day, 12)
        self.assertEqual(dt.year, 2020)
        self.assertEqual(dt.minute, 14)
        self.assertEqual(dt.second, 15)

    def test_localized_utc_string(self):
        iso_string="2020-11-12T13:14:15+02:00"
        dt=get_utc_datetime_from_iso8601_string(iso_string)
        #dt=datetime()

        self.assertEqual(dt.hour, 11)
        self.assertEqual(dt.day, 12)
        self.assertEqual(dt.year, 2020)
        self.assertEqual(dt.minute, 14)
        self.assertEqual(dt.second, 15)

if __name__ == '__main__':
    unittest.main()
