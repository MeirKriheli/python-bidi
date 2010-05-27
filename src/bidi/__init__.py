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
    """Will be used to create the console script"""

    import optparse
    import sys

    parser = optparse.OptionParser()

    parser.add_option('-e', '--encoding',
                      dest='encoding',
                      default='utf-8',
                      type='string',
                      help='Text encoding (default: utf-8)')

    parser.add_option('-u', '--upper-is-rtl',
                      dest='upper_is_rtl',
                      default=False,
                      action='store_true',
                      help="treat upper case chars as strong 'R' "
                        'for debugging (default: False).')
    options, rest = parser.parse_args()

    if rest:
        sys.stdout.write(get_display(rest[0], options.encoding, options.upper_is_rtl))
    else:
        for line in sys.stdin:
            sys.stdout.write(get_display(line, options.encoding, options.upper_is_rtl))
