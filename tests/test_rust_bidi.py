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

from bidi import get_base_level, get_display

# keep as list with char per line to prevent browsers from changing display order
HELLO_HEB_LOGICAL = "".join(["ש", "ל", "ו", "ם"])

HELLO_HEB_DISPLAY = "".join(
    [
        "ם",
        "ו",
        "ל",
        "ש",
    ]
)


class TestRustBidiAlgorithm(unittest.TestCase):
    "Tests the Rust based bidi algorithm"

    def test_surrogate(self):
        """Test surrogate pairs"""

        text = HELLO_HEB_LOGICAL + " \U0001d7f612"

        display = get_display(text)
        self.assertEqual(display, "\U0001d7f612 " + HELLO_HEB_DISPLAY)

    def test_override_base_dir(self):
        """Tests overriding the base paragraph direction"""

        # normally the display should be :MOLAHS be since we're overriding the
        # base dir the colon should be at the end of the display
        storage = f"{HELLO_HEB_LOGICAL}:"
        display = f"{HELLO_HEB_DISPLAY}:"

        self.assertEqual(get_display(storage, base_dir="L"), display)

    def test_output_encoding(self):
        """Make sure the display is in the same encoding as the incoming text"""

        storage = b"\xf9\xec\xe5\xed"  # Hebrew word shalom in cp1255
        display = b"\xed\xe5\xec\xf9"

        self.assertEqual(get_display(storage, encoding="cp1255"), display)

    def test_mixed_hebrew_numbers_issue10(self):
        """Test for the case reported in https://github.com/MeirKriheli/python-bidi/issues/10"""

        tests = (
            (
                "1 2 3 \u05E0\u05D9\u05E1\u05D9\u05D5\u05DF",
                "\u05DF\u05D5\u05D9\u05E1\u05D9\u05E0 3 2 1",
            ),
            (
                "1 2 3 123 \u05E0\u05D9\u05E1\u05D9\u05D5\u05DF",
                "\u05DF\u05D5\u05D9\u05E1\u05D9\u05E0 123 3 2 1",
            ),
        )
        for storage, display in tests:
            self.assertEqual(get_display(storage), display)

    def test_get_base_level(self):
        """Test base dir"""

        self.assertEqual(get_base_level(HELLO_HEB_LOGICAL), 1)
        self.assertEqual(get_base_level("Hello"), 0)


if __name__ == "__main__":
    unittest.main()
