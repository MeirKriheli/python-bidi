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

"""Stress the Rust extension from multiple threads (free-threaded / GIL builds)."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import unittest

from bidi import get_display

HELLO_HEB_LOGICAL = "".join(["ש", "ל", "ו", "ם"])
HELLO_HEB_DISPLAY = "".join(["ם", "ו", "ל", "ש"])


class TestConcurrentRustBidi(unittest.TestCase):
    """Concurrent calls into the native module."""

    def test_concurrent_get_display(self):
        text = HELLO_HEB_LOGICAL + " \U0001d7f612"
        expected = "\U0001d7f612 " + HELLO_HEB_DISPLAY

        def work():
            return get_display(text)

        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = [pool.submit(work) for _ in range(64)]
            for f in as_completed(futures):
                self.assertEqual(f.result(), expected)
