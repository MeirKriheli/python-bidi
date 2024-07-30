# This file is part of python-bidi
#
# python-bidi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Copyright (C) 2008-2010 Yaacov Zamir <kzamir_a_walla.co.il>,
# Meir kriheli <meir@mksoft.co.il>
"""BiDi algorithm unit tests"""

import unittest

from bidi.algorithm import get_display, get_embedding_levels, get_empty_storage


class TestPythonBidiAlgorithm(unittest.TestCase):
    "Tests the Python based bidi algorithm (based on GNU fribidi ones)"

    def test_surrogate(self):
        """Test for storage and base levels in case of surrogate pairs"""

        storage = get_empty_storage()

        text = 'HELLO \U0001d7f612'
        get_embedding_levels(text, storage, upper_is_rtl=True)

        # should return 9, not 10 even in --with-unicode=ucs2
        self.assertEqual(len(storage['chars']), 9)

        # Is the expected result ? should be EN
        _ch = storage['chars'][6]
        self.assertEqual(_ch['ch'], '\U0001d7f6')
        self.assertEqual(_ch['type'], 'EN')

        display = get_display(text, upper_is_rtl=True)
        self.assertEqual(display, '\U0001d7f612 OLLEH')

    def test_implict_with_upper_is_rtl(self):
        '''Implicit tests'''

        tests = (
            ('car is THE CAR in arabic', 'car is RAC EHT in arabic'),
            ('CAR IS the car IN ENGLISH', 'HSILGNE NI the car SI RAC'),
            ('he said "IT IS 123, 456, OK"', 'he said "KO ,456 ,123 SI TI"'),
            ('he said "IT IS (123, 456), OK"',
             'he said "KO ,(456 ,123) SI TI"'),
            ('he said "IT IS 123,456, OK"', 'he said "KO ,123,456 SI TI"'),
            ('he said "IT IS (123,456), OK"',
             'he said "KO ,(123,456) SI TI"'),
            ('HE SAID "it is 123, 456, ok"', '"it is 123, 456, ok" DIAS EH'),
            ('<H123>shalom</H123>', '<123H/>shalom<123H>'),
            ('<h123>SAALAM</h123>', '<h123>MALAAS</h123>'),
            ('HE SAID "it is a car!" AND RAN',
             'NAR DNA "!it is a car" DIAS EH'),
            ('HE SAID "it is a car!x" AND RAN',
             'NAR DNA "it is a car!x" DIAS EH'),
            ('SOLVE 1*5 1-5 1/5 1+5', '1+5 1/5 1-5 5*1 EVLOS'),
            ('THE RANGE IS 2.5..5', '5..2.5 SI EGNAR EHT'),
            ('-2 CELSIUS IS COLD', 'DLOC SI SUISLEC 2-'),
        )

        for storage, display in tests:
            self.assertEqual(get_display(storage, upper_is_rtl=True), display)

    def test_override_base_dir(self):
        """Tests overriding the base paragraph direction"""

        # normally the display should be :MOLAHS be since we're overriding the
        # base dir the colon should be at the end of the display
        storage = 'SHALOM:'
        display = 'MOLAHS:'

        self.assertEqual(get_display(storage, upper_is_rtl=True, base_dir='L'),
                         display)

    def test_output_encoding(self):
        """Make sure the display is in the same encoding as the incoming text"""

        storage = b'\xf9\xec\xe5\xed'  # Hebrew word shalom in cp1255
        display = b'\xed\xe5\xec\xf9'

        self.assertEqual(get_display(storage, encoding='cp1255'), display)

    def test_explicit_with_upper_is_rtl(self):
        """Explicit tests"""
        tests = (
            ('this is _LJUST_o', 'this is JUST'),
            ('a _lsimple _RteST_o th_oat', 'a simple TSet that'),
            ('HAS A _LPDF missing', 'PDF missing A SAH'),
            ('AnD hOw_L AbOuT, 123,987 tHiS_o',
             'w AbOuT, 123,987 tHiSOh DnA'),
            ('a GOOD - _L_oTEST.', 'a TSET - DOOG.'),
            ('here_L is_o_o_o _R a good one_o', 'here is eno doog a '),
            ('THE _rbest _lONE and', 'best ENO and EHT'),
            ('A REAL BIG_l_o BUG!', '!GUB GIB LAER A'),
            ('a _L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_L_Rbug',
             'a gub'),
            # FIXME the following commented explicit test fails
            # (u'AN ARABIC _l_o 123-456 NICE ONE!',
            #  u'!ENO ECIN 456-123  CIBARA NA'),
            ('AN ARABIC _l _o 123-456 PAIR', 'RIAP   123-456 CIBARA NA'),
            ('this bug 67_r_o89 caught!', 'this bug 6789 caught!'),
        )

        # adopt fribidi's CapRtl encoding
        mappings = {
            '_>': "\u200E",  # LRM
            '_<': "\u200F",  # RLM
            '_l': "\u202A",  # LRE
            '_r': "\u202B",  # RLE
            '_o': "\u202C",  # PDF
            '_L': "\u202D",  # LRO
            '_R': "\u202E",  # RLO
            '__': '_',
        }

        for storage, display in tests:
            for key, val in mappings.items():
                storage = storage.replace(key, val)
            self.assertEqual(get_display(storage, upper_is_rtl=True), display)

    def test_mixed_hebrew_numbers_issue10(self):
        """Test for the case reported in
        https://github.com/MeirKriheli/python-bidi/issues/10
        """
        tests = (
            ('1 2 3 \u05E0\u05D9\u05E1\u05D9\u05D5\u05DF', '\u05DF\u05D5\u05D9\u05E1\u05D9\u05E0 3 2 1'),
            ('1 2 3 123 \u05E0\u05D9\u05E1\u05D9\u05D5\u05DF', '\u05DF\u05D5\u05D9\u05E1\u05D9\u05E0 123 3 2 1'),
        )
        for storage, display in tests:
            self.assertEqual(get_display(storage), display)


if __name__ == '__main__':
    unittest.main()
