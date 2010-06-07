python-bidi
=================

`Bi-directional`_ (BiDi) layout implementation in pure python

.. _Bi-directional: http://en.wikipedia.org/wiki/Bi-directional_text


API
----

The algorithm starts with a single entry point `bidi.algorithm.get_display`.

**Required arguments:**

* ``unicode_or_str``: The orginal unicode or string (i.e: storage). If it's a string
  use the optional argument ``encoding`` to specify it's encoding.

**Optional arguments:**

* ``encoding``: If unicode_or_str is a string, specifies the encdoing. The
  algorithm uses unicodedata_ which requires unicode. This encoding will be
  used to decode and encode back to string before returning
  (default: "utf-8").

* ``upper_is_rtl``: True to treat upper case chars as strong 'R' for
  debugging (default: False).

* ``debug``: True to display (using `sys.stderr`_) the steps taken with the
  algorithm (default: False).

Returns the display layout, either as unicode or ``encoding`` encoded string
(depending on the type of ``unicode_or_str'``).

.. _unicodedata: http://docs.python.org/library/unicodedata.html
.. _sys.stderr: http://docs.python.org/library/sys.html?highlight=sys.stderr#sys.stderr

Example::

    >>> from bidi.algorithm import get_display
    >>> get_display(u'car is THE CAR in arabic', upper_is_rtl=True)
    u'car is RAC EHT in arabic'


CLI
----

``pybidi`` is a command line utility (calling  ``bidi.main``) for running the
bidi algorithm. the script can get a string as a parameter or read text from
`stdin`. Usage::

    $ pybidi -h
    Usage: pybidi [options]

    Options:
      -h, --help            show this help message and exit
      -e ENCODING, --encoding=ENCODING
                            Text encoding (default: utf-8)
      -u, --upper-is-rtl    treat upper case chars as strong 'R' for debugging
                            (default: False).
      -d, --debug           Display the steps taken with the algorithm

Examples::

    $ pybidi -u 'car is THE CAR in arabic'
    car is RAC EHT in arabic

    $ cat ~/Documents/example.txt | pybidi
    ...

Installation
-------------

See ``docs/INSTALL.rst``

Running tests
--------------

To run the tests::

    python -m bidi.tests

Some explicit tests are failing right now (see TODO)

