import unittest

from demo import add

class TestAdd(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(3, 5), 8)
        self.assertEqual(add(-1, 1), 0)
        self.assertNotEqual(add(2, 2), 5)

# python -m unittest 会自动执行 test*.py 里的 Test* 类
