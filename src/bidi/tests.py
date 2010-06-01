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

    def test_explicit_with_upper_is_rtl(self):
        """Explicit tests"""
        tests = (
            (u'this is _LJUST_o', u'this is JUST'),
            (u'a _lsimple _RteST_o th_oat', u'a simple TSet that'),
            (u'HAS A _LPDF missing', u'PDF missing A SAH'),
            (u'AnD hOw_L AbOuT, 123,987 tHiS_o', u'w AbOuT, 123,987 tHiSOh DnA'),
            (u'a GOOD - _L_oTEST.', u'a TSET - DOOG.'),
            #(u'here_L is_o_o_o _R a good one_o', u'here is eno doog a'),
            #(u'And _r 123,987_LTHE_R next_o oNE:', u'987THEtxen  oNE:,123  ndA'),
            #(u'_R_r and the last _LONE_o IS', u'SI and the last ONE'),
            (u'THE _rbest _lONE and', u'best ENO and EHT'),
            (u'A REAL BIG_l_o BUG!', u'!GUB GIB LAER A'),
            (u'a _L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_Rbug', u'a gub'),
            #(u'AN ARABIC _l_o 123-456 NICE ONE!', u'!ENO ECIN 456-123  CIBARA NA'),
            (u'AN ARABIC _l _o 123-456 PAIR', u'RIAP   123-456 CIBARA NA'),
            (u'this bug 67_r_o89 catched!', u'this bug 6789 catched!'),
        )

        # adopt fribidi's CapRtl encoding
        mappings = {
            u'_>': u"\u200E",
            u'_<': u"\u200F",
            u'_l': u"\u202A",
            u'_r': u"\u202B",
            u'_o': u"\u202C",
            u'_L': u"\u202D",
            u'_R': u"\u202E",
            u'__': '_',
        }

        for storage, display in tests:
            for key, val in mappings.items():
                storage = storage.replace(key, val)
            self.assertEqual(get_display(storage, upper_is_rtl=True), display)


if __name__ == '__main__':
    unittest.main()
