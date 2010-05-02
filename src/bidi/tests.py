import unittest
from bidi import do_bidi

class TestBidiAlgorithm(unittest.TestCase):

    def test_with_upper_is_rtl(self):
        '''Tests from http://imagic.weizmann.ac.il/~dov/freesw/FriBidi/ '''

        self.assertEqual(do_bidi(u'car is THE CAR in arabic', True),
                    u'car is RAC EHT in arabic')

        self.assertEqual(do_bidi(u'CAR IS the car IN ENGLISH', True),
                    u'HSILGNE NI the car SI RAC')
        #he said "IT IS 123, 456, OK"        => he said "KO ,456 ,123 SI TI"       
        #he said "IT IS (123, 456), OK"      => he said "KO ,(456 ,123) SI TI"     
        #he said "IT IS 123,456, OK"         => he said "KO ,123,456 SI TI"        
        #he said "IT IS (123,456), OK"       => he said "KO ,(123,456) SI TI"      
        #HE SAID "it is 123, 456, ok"        =>        "it is 123, 456, ok" DIAS EH
        #<H123>shalom</H123>                 =>                 <123H/>shalom<123H>
        #<h123>SAALAM</h123>                 => <h123>MALAAS</h123>                
        #HE SAID "it is a car!" AND RAN      =>      NAR DNA "!it is a car" DIAS EH
        #HE SAID "it is a car!x" AND RAN     =>     NAR DNA "it is a car!x" DIAS EH
        #-2 CELSIUS IS COLD                  =>                  DLOC SI SUISLEC -2
        #SOLVE 1*5 1-5 1/5 1+5               =>               1+5 1/5 1-5 5*1 EVLOS
        #THE RANGE IS 2.5..5                 =>                 5..2.5 SI EGNAR EH

if __name__ == '__main__':
    unittest.main()
