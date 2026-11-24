import unittest
from s_alpha.fusion_calculator import calculate
class FusionCalculatorTests(unittest.TestCase):
    def test_contract(self):
        for a,op,b,want in [("0.1","+","0.2","0.3"),("7","-","9","-2"),("6","*","7","42"),("9","/","4","2.25")]:
            self.assertEqual(calculate(a,op,b),want)
    def test_invalid(self):
        for a,op,b in [("1","/","0"),("NaN","+","2"),("1e999","+","2"),("1","**","2")]:
            with self.assertRaises(ValueError):
                calculate(a,op,b)
