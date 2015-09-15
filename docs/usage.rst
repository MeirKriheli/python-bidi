========
Usage
========

To use Python BiDi in a project::

.. code-block:: python

    from bidi import algorithm

    some_string = 'your string goes here'
    result = algorithm.get_display(some_string)
