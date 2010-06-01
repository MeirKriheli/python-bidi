"""BiDi algorithm unit tests"""

import unittest
from bidi.algorithm import get_display

class TestBidiAlgorithm(unittest.TestCase):
    "Tests the bidi algorithm"

    def test_implict_with_upper_is_rtl(self):
        '''Tests from GNU fribidi '''

        storage = u'car is THE CAR in arabic'
        display = u'car is RAC EHT in arabic'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'CAR IS the car IN ENGLISH'
        display = u'HSILGNE NI the car SI RAC'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'he said "IT IS 123, 456, OK"'
        display = u'he said "KO ,456 ,123 SI TI"'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'he said "IT IS (123, 456), OK"'
        display = u'he said "KO ,(456 ,123) SI TI"'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'he said "IT IS 123,456, OK"'
        display = u'he said "KO ,123,456 SI TI"'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'he said "IT IS (123,456), OK"'
        display = u'he said "KO ,(123,456) SI TI"'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'HE SAID "it is 123, 456, ok"'
        display = u'"it is 123, 456, ok" DIAS EH'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'<H123>shalom</H123>'
        display = u'<123H/>shalom<123H>'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'<h123>SAALAM</h123>'
        display = u'<h123>MALAAS</h123>'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'HE SAID "it is a car!" AND RAN'
        display = u'NAR DNA "!it is a car" DIAS EH'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'HE SAID "it is a car!x" AND RAN'
        display = u'NAR DNA "it is a car!x" DIAS EH'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'SOLVE 1*5 1-5 1/5 1+5'
        display = u'1+5 1/5 1-5 5*1 EVLOS'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'THE RANGE IS 2.5..5'
        display = u'5..2.5 SI EGNAR EHT'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'-2 CELSIUS IS COLD'
        display = u'DLOC SI SUISLEC 2-'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'''DID YOU SAY '\u202Ahe said "\u202Bcar MEANS CAR\u202C"\u202C'?'''
        display = u'''?'he said "RAC SNAEM car"' YAS UOY DID'''
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

if __name__ == '__main__':
    unittest.main()
