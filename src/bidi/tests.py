import unittest
import unicodedata
from bidi.paragraph import Paragraph
from bidi import get_display

class TestBidiAlgorithm(unittest.TestCase):

    def test_paragraph_level(self):
        '''Test P2 and P3 implemntation'''

        p = Paragraph(u'car is THE CAR in arabic', upper_is_rtl=True)
        p.set_storage_and_level()

        self.assertEqual(p.level, 0)

        p = Paragraph(u'<H123>shalom</H123>', upper_is_rtl=True)
        p.set_storage_and_level()
        self.assertEqual(p.level, 1)

        p = Paragraph(u'123 \u05e9\u05dc\u05d5\u05dd')
        p.set_storage_and_level()
        self.assertEqual(p.level, 1)

    def test_with_upper_is_rtl(self):
        '''Tests from http://imagic.weizmann.ac.il/~dov/freesw/FriBidi/ '''

        storage = u'car is THE CAR in arabic'
        display = u'car is RAC EHT in arabic'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'CAR IS the car IN ENGLISH'
        display = u'HSILGNE NI the car SI RAC'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'he said "IT IS 123, 456, OK"'
        display = u'he said "KO ,456 ,123 SI TI"'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'he said "IT IS (123, 456), OK"'
        #display = u'he said "KO ,(456 ,123) SI TI"'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'he said "IT IS 123,456, OK"'
        #display = u'he said "KO ,123,456 SI TI"'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'he said "IT IS (123,456), OK"'
        #display = u'he said "KO ,(123,456) SI TI"'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'HE SAID "it is 123, 456, ok"'
        #display = u'"it is 123, 456, ok" DIAS EH'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'<H123>shalom</H123>',
        #display = u'<123H/>shalom<123H>'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'<h123>SAALAM</h123>'
        #display = u'<h123>MALAAS</h123>'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'HE SAID "it is a car!" AND RAN'
        #display = u'NAR DNA "!it is a car" DIAS EH'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'HE SAID "it is a car!x" AND RAN'
        #display = u'NAR DNA "it is a car!x" DIAS EH'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'SOLVE 1*5 1-5 1/5 1+5'
        #display = u'1+5 1/5 1-5 5*1 EVLOS'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        #storage = u'THE RANGE IS 2.5..5'
        #display = u'5..2.5 SI EGNAR EHT'
        #self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'-2 CELSIUS IS COLD'
        display = u'DLOC SI SUISLEC -2'
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

        storage = u'''DID YOU SAY '\u202Ahe said "\u202Bcar MEANS CAR\u202C"\u202C'?'''
        display = u'''?'he said "RAC SNAEM car"' YAS UOY DID'''
        self.assertEqual(get_display(storage, upper_is_rtl=True), display)

if __name__ == '__main__':
    unittest.main()
