Changelog
==========

.. :changelog:

0.6.6
-----

* Upgraded to macos-13 runner (as 12 is not available anymore).


0.6.5
-----

* Revert "Added pypy3.11 to build"


0.6.4
-----

* Added pypy3.11 to build
* Removed pypy3.8 from build, not suppurted
* Bumped pyo3 to 0.23.3, drops pypy3.7 and pypy3.8
* Bumped unicode-bidi to 0.3.18  closes #28


0.6.3
-----

* Updated pyo3 to 0.22.4
* Python 3.13 wheels are finally working

0.6.2
-----

* Added check-latest to the build

0.6.1
-----

* Bumped to build Python 3.13 wheels

0.6.0
-----

* Added implemention selection (Python or Rust) to pybidi cli,
  respecting backward comapt
* Restored older algorithm, supports both implementations closes #25
* Modernize and simplify Python code (Thanks Christian Clauss)

0.5.2
-----

* Added get_base_level backward compat
* docstring cleanup

0.5.1
-------

* Added compat for older import, closes #23
* Updated copyrights


0.5.0
-----

Backwards incompatible changes!

* Switched to using Rust based unicode-bidi using PyO3
* Dropped Python < 3.9 support
* Removed "upper_is_rtl"
* Import of ``get_display`` changed to ``from bidi import get_display``


0.4.2
-----

* Type Fixes, thanks jwilk


0.4.1
-----

* Merged Fix for mixed RTL and numbers, Thanks Just van Rossum

0.4.0
-----

* Move to cookiecutter template
* Python 3 support (py2.6, 2.7, 3.3, 3.4 and pypy)
* Better docs
* Travis integration
* Tox tests
* PEP8 cleanup

0.3.4
------

* Remove extra newline in console script output

0.3.3
------

* Implement overriding base paragraph direction
* Allow overriding base direction in pybidi console script
* Fix returning display in same encoding

0.3.2
------

* Test for surrogate pairs
* Fix indentation in documentations
* Specify license in setup.py

0.3.1
-----

* Added missing description
* docs/INSTALL.rst

0.3
---

* Apply bidi mirroring
* Move to back function based implementation

0.2
---

* Move the algorithm to a class based implementation

0.1
---

* Initial release
