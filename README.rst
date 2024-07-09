===============================
Python BiDi
===============================

.. image:: https://badge.fury.io/py/python-bidi.png
    :target: http://badge.fury.io/py/python-bidi

`Bi-directional`_ (BiDi) layout for Python, wrapping the `unicode-bidi`_ crate.

`Package documentation`_

.. _Bi-directional: http://en.wikipedia.org/wiki/Bi-directional_text
.. _unicode-bidi: https://crates.io/crates/unicode-bidi
.. _Package documentation: http://python-bidi.readthedocs.org/en/latest/


API
----

The algorithm starts with a single entry point `bidi.get_display`.

**Required arguments:**

* ``str_or_bytes``: The string or bytes (i.e.: storage). If it's bytes
  use the optional argument ``encoding`` to specify it's encoding.

**Optional arguments:**

* ``encoding``: If unicode_or_str is a string, specifies the encoding. The
  algorithm uses unicodedata_ which requires unicode. This encoding will be
  used to decode and encode back to string before returning
  (default: "utf-8").

* ``base_dir``:  ``'L'`` or ``'R'``, override the calculated base_level.

* ``debug``: ``True`` to display the Unicode levels as seen by the algorithm
  (default: ``False``).

Returns the display layout, either as ``str`` or ``encoding`` encoded ``bytes``
(depending on the type of ``str_or_bytes'``).

.. _unicodedata: http://docs.python.org/library/unicodedata.html

Example::

    >>> from bidi import get_display
    >>> # keep as list with char per line to prevent browsers from changing display order
    >>> HELLO_HEB = "".join([
    ...     "ש",
    ...     "ל",
    ...     "ו",
    ...     "ם"
    ... ])
    >>>
    >>> HELLO_HEB_DISPLAY = "".join([
    ...     "ם",
    ...     "ו",
    ...     "ל",
    ...     "ש",
    ... ])
    >>>
    >>> get_display(HELLO_HEB) == HELLO_HEB_DISPLAY
    True


CLI
----

``pybidi`` is a command line utility (calling  ``bidi.main``) for running the
display algorithm. The script can get a string as a parameter or read text from
`stdin`.

Usage::

    $ pybidi -h
    usage: pybidi [-h] [-e ENCODING] [-d] [-b {L,R}]

    options:
      -h, --help            show this help message and exit
      -e ENCODING, --encoding ENCODING
                            Text encoding (default: utf-8)
      -d, --debug           Output to stderr steps taken with the algorithm
      -b {L,R}, --base-dir {L,R}
                            Override base direction [L|R]

Examples::

    $ pybidi -u 'Your string here'
    $ cat ~/Documents/example.txt | pybidi


Installation
-------------

See ``docs/INSTALL.rst``

Running tests
--------------

To run the tests::

    pip install nox
    nox
