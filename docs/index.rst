.. complexity documentation master file, created by
   sphinx-quickstart on Tue Jul  9 22:26:36 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Python BiDi's documentation!
=======================================

`Bi-directional`_ (BiDi) layout implementation in pure python.

.. _Bi-directional: http://en.wikipedia.org/wiki/Bi-directional_text

Installation
------------

At the command line (assuming you're using some virtualenv)::

    pip install python-bidi


Usage
--------

To use Python BiDi in a project:

.. code-block:: python

    import bidi

    some_string = "your string goes here"
    result = bidi.get_display(some_string)


Versions 0.5.1 and 0.5.2 adds compat for the older import path:

.. code-block:: python

    from bidi import get_display


Contents:

.. toctree::
   :maxdepth: 2

   contributing
   authors
   bidi
   history

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
