# -*- coding: utf-8 -*-

import find_nearer_stores as target
import unittest


class TestFindNearerStores(unittest.TestCase):
    def test_complete_zipcode(self):
        self.assertEqual('02700', target.complete_zipcode('2700'))
        self.assertEqual('00520', target.complete_zipcode('520'))
        self.assertEqual('75012', target.complete_zipcode('75012'))

    def test_get_valid_addr(self):
        self.assertEqual('RUE A 75012', target.get_valid_addr(float('nan'), 'RUE A', '75012'))
        self.assertEqual('RUE A 75012', target.get_valid_addr(0, 'RUE A', '75012'))
        self.assertEqual('7-9 RUE A 75012', target.get_valid_addr(7.0, '9 RUE A', '75012'))
        self.assertEqual('7-9 RUE A 75012', target.get_valid_addr(7, 'A 9 RUE A', '75012'))
        self.assertEqual('7 RUE A 75012', target.get_valid_addr(7, 'RUE A', '75012'))

if __name__ == '__main__':
    unittest.main()