#!/usr/bin/env python

import wrangler
import unittest

class TestLassoAPI(unittest.TestCase):
    def setUp(self):
        self.lasso = wrangler.Lasso()
        self.lasso.connect()

    def test_next_task(self):
        task = self.lasso.next_task()
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
