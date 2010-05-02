import unittest
import unicodedata
from bidi import do_bidi
from bidi.algorithm import bidirectional_uppercase_rtl, paragraph_level

class TestBidiAlgorithm(unittest.TestCase):

    def testbidirectional_uppercase_rtl(self):
        '''Tests treating upper case as RTL type'''
        self.assertEqual(bidirectional_uppercase_rtl(u'A'), 'R')
        self.assertEqual(bidirectional_uppercase_rtl(u'a'), 'L')

        alef = unicodedata.lookup('HEBREW LETTER ALEF')
        self.assertEqual(bidirectional_uppercase_rtl(alef), 'R')

    def test_paragraph_level(self):
        '''Test P2 and P3 implemntation'''
        
        self.assertEqual(paragraph_level(u'car is THE CAR in arabic'), 0)

        self.assertEqual(paragraph_level(u'<H123>shalom</H123>',
                                         bidirectional_uppercase_rtl), 1)
        
        self.assertEqual(paragraph_level(u'123 \u05e9\u05dc\u05d5\u05dd'), 1)

    def test_with_upper_is_rtl(self):
        '''Tests from http://imagic.weizmann.ac.il/~dov/freesw/FriBidi/ '''

        self.assertEqual(do_bidi(u'car is THE CAR in arabic', True),
                    u'car is RAC EHT in arabic')

        self.assertEqual(do_bidi(u'CAR IS the car IN ENGLISH', True),
                    u'HSILGNE NI the car SI RAC')

        self.assertEqual(do_bidi(u'he said "IT IS 123, 456, OK"', True),
                    u'he said "KO ,456 ,123 SI TI"')

        self.assertEqual(do_bidi(u'he said "IT IS (123, 456), OK"', True),
                    u'he said "KO ,(456 ,123) SI TI"')

        self.assertEqual(do_bidi(u'he said "IT IS 123,456, OK"', True),
                    u'he said "KO ,123,456 SI TI"')

        self.assertEqual(do_bidi(u'he said "IT IS (123,456), OK"', True),
                    u'he said "KO ,(123,456) SI TI"')

        self.assertEqual(do_bidi(u'HE SAID "it is 123, 456, ok"', True),
                    u'"it is 123, 456, ok" DIAS EH')

        self.assertEqual(do_bidi(u'<H123>shalom</H123>',True),
                    u'<123H/>shalom<123H>')

        self.assertEqual(do_bidi(u'<h123>SAALAM</h123>', True),
                    u'<h123>MALAAS</h123>')

        self.assertEqual(do_bidi(u'HE SAID "it is a car!" AND RAN', True),
                    u'NAR DNA "!it is a car" DIAS EH')

        self.assertEqual(do_bidi(u'HE SAID "it is a car!x" AND RAN', True),
                    u'NAR DNA "it is a car!x" DIAS EH')

        self.assertEqual(do_bidi(u'SOLVE 1*5 1-5 1/5 1+5', True),
                    u'1+5 1/5 1-5 5*1 EVLOS')

        self.assertEqual(do_bidi(u'THE RANGE IS 2.5..5', True),
                    u'5..2.5 SI EGNAR EHT')

        self.assertEqual(do_bidi(u'-2 CELSIUS IS COLD', True),
                    u'DLOC SI SUISLEC -2')

if __name__ == '__main__':
    unittest.main()
