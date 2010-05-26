#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

"""
Implementation of Unicode Bidirectional Algorithm
http://www.unicode.org/unicode/reports/tr9/
test cases from http://imagic.weizmann.ac.il/~dov/freesw/FriBidi/
"""

def get_display(unicode_or_str, encoding='utf-8', upper_is_rtl=False):
    """Accepts unicode or string. In case it's a string, `encoding`
    is needed as it works on unicode ones (default:"utf-8").

    Set `upper_is_rtl` to True to treat upper case chars as strong 'R'
    for debugging (default: False).

    """
    from paragraph import Paragraph

    return Paragraph(unicode_or_str, encoding, upper_is_rtl).get_display()

def main():

    if len(sys.argv) == 2:
        print do_bidi(unicode(sys.argv[1], 'utf-8'), False)
        sys.exit(0)

    if len(sys.argv) == 3 and sys.argv[2] == '--capsrtl':
        print do_bidi(unicode(sys.argv[1], 'utf-8'), True)
        sys.exit(0)

    if len(sys.argv) == 3 and sys.argv[2] == '--debug':
        debug_string(unicode(sys.argv[1], 'utf-8'), False)
        sys.exit(0)

    if len(sys.argv) == 4 and (sys.argv[2] == '--debug' or sys.argv[3] == '--debug') \
            and (sys.argv[2] == '--capsrtl' or sys.argv[3] == '--capsrtl'):
        debug_string(unicode(sys.argv[1], 'utf-8'), True)
        sys.exit(0)

    print
    print
    print 'usage: pybidi.py "string" [--caprtl] [--debug]'
    print 'caprtl - Caps Latin chars are rtl (testing)'
    print 'debug - Show algorithm steps'

    sys.exit(1)

if __name__ == "__main__":
    main()
