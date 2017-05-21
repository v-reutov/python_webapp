from django.test import TestCase
from sqrt_platform.core.sqrt import *
# Create your tests here.


class CoreSqrtTestCase(TestCase):
    def test_int(self):
        self.assertEqual(get_sqrt('4'), '2')

    def test_complex(self):
        self.assertEqual(get_sqrt('-1'), 'i')
        self.assertEqual(get_sqrt('14+5i'),
                         '3.79908335966181 + 0.658053473252176i')

    def test_float(self):
        self.assertEqual(get_sqrt('2'), '1.4142135623730951')
        self.assertEqual(get_sqrt('5'), '2.23606797749979')

    def test_precision(self):
        self.assertEqual(get_sqrt('2', 5), '1.4142')
        self.assertEqual(get_sqrt('1234', 9), '35.1283361')
