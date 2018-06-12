"""Setup configuration for OWData package.

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
from io import open  # 2.7 only

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='OWData',
    version='0.0.1',
    description='An API for accessing synoptic-timescale reanalyis data',

    # From README - see above
    long_description=long_description,

    url='https://brohan.org/OWData/',

    author='Philip Brohan',
    author_email='philip.brohan@metofice.gov.uk',

    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Atmospheric Science',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
    ],

    # Keywords for your project. What does your project relate to?
    keywords='weather reanalysis 20cr cera20c era5',

    # Automatically find the software to be included
    packages=find_packages(),

    # Tests are in OWData/tests organised as a module
    # (a unittest.TestSuite - just put __init__.py in all directories).
    # Name the module not the file here ('.' not '/').
    test_suite="OWData.tests",

    # Other packages that your project depends on.
    # iris>2 - does not work - can't find any iris?
    install_requires=[
        'numpy>1.13',
        'scipy>0.18',
        'pandas>0.20',
        'ecmwf-api-client>1.4',
    ],

    # other relevant URLs.
    #project_urls={ 
    #    'Bug Reports': 'https://github.com/philip-brohan/OWData/issues',
    #    'Source': 'https://github.com/philip-brohan/OWData',
    #},
)