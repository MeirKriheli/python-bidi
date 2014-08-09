#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

requirements = [
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name="python-bidi",
    version="0.3.4",
    url='http://github.com/mksoft/python-bidi',
    description='BiDi layout implementation in pure python',
    long_description=readme + '\n\n' + history,
    author='Meir Kriheli',
    author_email='mkriheli@gmail.com',
    packages=[
        'bidi',
    ],
    package_dir={
        'bidi': 'bidi'
    },
    include_package_data=True,
    install_requires=requirements,
    entry_points={
        'console_scripts': 'pybidi = bidi:main'
    },
    license='http://www.gnu.org/licenses/lgpl.html',
    zip_safe=False,
    keywords='bidi unicode layout',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Text Processing',
    ],
    test_suite='tests',
    tests_require=test_requirements,
)
