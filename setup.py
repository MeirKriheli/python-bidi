import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "python-bidi",
    version = "0.3.2",
    url = 'http://github.com/mksoft/python-bidi',
    description = 'BiDi layout implementation in pure python',
    long_description = read('README.rst') + read('CHANGELOG.rst') + read('TODO.rst'),
    license = 'http://www.gnu.org/licenses/lgpl.html',
    author = 'Meir Kriheli',
    author_email = 'meir@mksoft.co.il',

    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,

    install_requires = ['setuptools'],

    entry_points = {
        'console_scripts': 'pybidi = bidi:main'
    },

    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Text Processing',
    ]
)
