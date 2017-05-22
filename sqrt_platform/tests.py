from django.test import TestCase
from sqrt_platform.core.sqrt import get_sqrt
from sqrt_platform.core.wolfram import get_sqrt as get_sqrt_ex
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

    def test_expression(self):
        self.assertEqual(get_sqrt_ex('a ** 2'), 'a')
        self.assertEqual(get_sqrt_ex('1 - sin(x) ** 2'), 'abs(cos(x))')
