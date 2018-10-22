"""Setup configuration for IRData package.

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
    name='IRData',
    version='0.2.0',
    description='An API for accessing synoptic-timescale reanalyis data',

    # From README - see above
    long_description=long_description,

    url='https://brohan.org/IRData/',

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
    test_suite="IRData.tests",

    # Other packages that your project depends on.
    install_requires=[
        'scitools-iris>=2.2',
        'cartopy>=0.16',
        'numpy>=1.15.2',
        'scipy>=1.1.0',
        'pandas>=0.23.4',
        'ecmwf-api-client>1.4',
    ],

    # other relevant URLs.
    project_urls={ 
        'Bug Reports': 'https://github.com/philip-brohan/IRData/issues',
        'Source': 'https://github.com/philip-brohan/IRData',
    },
)
