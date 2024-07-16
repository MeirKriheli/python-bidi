#!/usr/bin/env python
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
# Copyright (C) 2010-2015 Meir kriheli <mkriheli@gmail.com>.
#

from typing import AnyStr, Optional

from .bidi import get_display_inner

VERSION = "0.5.0"


def get_display(
    str_or_bytes: AnyStr,
    encoding: str = "utf-8",
    base_dir: Optional[str] = None,
    debug: Optional[bool] = False,
) -> AnyStr:
    """Accepts string or bytes. In case of bytes, `encoding`
    is needed as the inner function expects a valid string (default:"utf-8").

    Set `upper_is_rtl` to True to treat upper case chars as strong 'R'
    for debugging (default: False).

    Set `base_dir` to 'L' or 'R' to override the calculated base_level.

    Set `debug` to True to return the calculated levels.

    Returns the display layout, either as unicode or `encoding` encoded
    string.

    """

    if isinstance(str_or_bytes, bytes):
        text = str_or_bytes.decode(encoding)
        was_decoded = True
    else:
        text = str_or_bytes
        was_decoded = False

    display = get_display_inner(text, base_dir, debug)

    if was_decoded:
        display = display.encode(encoding)

    return display


def main():
    """Will be used to create the console script"""

    import argparse
    import sys

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-e",
        "--encoding",
        dest="encoding",
        default="utf-8",
        type=str,
        help="Text encoding (default: utf-8)",
    )

    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        default=False,
        action="store_true",
        help="Output to stderr steps taken with the algorithm",
    )

    parser.add_argument(
        "-b",
        "--base-dir",
        dest="base_dir",
        choices=["L", "R"],
        default=None,
        type=str,
        help="Override base direction [L|R]",
    )

    options, rest = parser.parse_known_args()

    if rest:
        lines = rest
    else:
        lines = sys.stdin

    for line in lines:
        display = get_display(
            line,
            options.encoding,
            options.base_dir,
            options.debug,
        )
        # adjust the encoding as unicode, to match the output encoding
        if not isinstance(display, str):
            display = display.decode(options.encoding)

        print(display, end="")


if __name__ == "__main__":
    main()
