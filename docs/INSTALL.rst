Installing python-bidi
=======================

You have several options to install python-bidi:

    * With easy_install::

        easy_install python-bidi

    * Download the tarball and extract it and run setup.py::
        
        wget http://github.com/downloads/mksoft/python-bidi/python-bidi-0.3.tar.gz
        tar zxf python-bidi-0.3.tar.gz
        cd python-bidi-0.3
        python setup.py install

    * Development version - python-bidi is using ``git`` and ``buildout``::
        
        git clone git://github.com/mksoft/python-bidi.git
        cd python-bidi/
        python bootstrap.py
        bin/buildout

      Now you can run the tests, custom intrepreter or ``pybidi``::

        bin/python -m bidi.tests
        bin/pybidi -u 'car is THE CAR in arabic'

        
