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
# 2010-2014 Meir kriheli <meir@mksoft.co.il>
"Unicode algorithm definitions"

import sys

MAX_DEPTH = 125  # max dpeth as defined in version 7 of the algorithm
IS_UCS2 = sys.maxunicode == 65535  # on UCS2 care is needed for surrogate pairs
SURROGATE_MIN, SURROGATE_MAX = 55296, 56319  # D800, DBFF

PARAGRAPH_LEVELS = {
    'L': 0,
    'AL': 1,
    'R': 1,
}

ISOLATE_INITIATORS = ('LRI', 'RLI', 'FSI')
X9_REMOVED = ['RLE', 'LRE', 'RLO', 'LRO', 'PDF', 'BN']
