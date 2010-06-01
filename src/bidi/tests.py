"""BiDi algorithm unit tests"""

import unittest
from bidi.algorithm import get_display

class TestBidiAlgorithm(unittest.TestCase):
    "Tests the bidi algorithm (based on GNU fribidi ones)"

    def test_implict_with_upper_is_rtl(self):
        '''Implicit tests'''

        tests = (
            (u'car is THE CAR in arabic', u'car is RAC EHT in arabic'),
            (u'CAR IS the car IN ENGLISH', u'HSILGNE NI the car SI RAC'),
            (u'he said "IT IS 123, 456, OK"', u'he said "KO ,456 ,123 SI TI"'),
            (u'he said "IT IS (123, 456), OK"', u'he said "KO ,(456 ,123) SI TI"'),
            (u'he said "IT IS 123,456, OK"', u'he said "KO ,123,456 SI TI"'),
            (u'he said "IT IS (123,456), OK"', u'he said "KO ,(123,456) SI TI"'),
            (u'HE SAID "it is 123, 456, ok"', u'"it is 123, 456, ok" DIAS EH'),
            (u'<H123>shalom</H123>', u'<123H/>shalom<123H>'),
            (u'<h123>SAALAM</h123>', u'<h123>MALAAS</h123>'),
            (u'HE SAID "it is a car!" AND RAN', u'NAR DNA "!it is a car" DIAS EH'),
            (u'HE SAID "it is a car!x" AND RAN', u'NAR DNA "it is a car!x" DIAS EH'),
            (u'SOLVE 1*5 1-5 1/5 1+5', u'1+5 1/5 1-5 5*1 EVLOS'),
            (u'THE RANGE IS 2.5..5', u'5..2.5 SI EGNAR EHT'),
            (u'-2 CELSIUS IS COLD', u'DLOC SI SUISLEC 2-'),
        )

        for storage, display in tests:
            self.assertEqual(get_display(storage, upper_is_rtl=True), display)



if __name__ == '__main__':
    unittest.main()
