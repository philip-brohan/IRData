"""Setup configuration for IRData package.

"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="IRData",
    version="0.3.0",
    description="An API for accessing synoptic-timescale reanalyis data",
    # From README - see above
    long_description=long_description,
    url="https://brohan.org/IRData/",
    author="Philip Brohan",
    author_email="philip.brohan@metofice.gov.uk",
    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.6",
    ],
    # Keywords for your project. What does your project relate to?
    keywords="weather reanalysis 20cr cera20c era5",
    # Automatically find the software to be included
    packages=find_packages(),
    # Tests are in OWData/tests organised as a module
    # (a unittest.TestSuite - just put __init__.py in all directories).
    # Name the module not the file here ('.' not '/').
    test_suite="IRData.tests",
    # Relies on iris (only installable by conda)
    # So dependencies managed externally in conda environment.
    install_requires=[],
    # other relevant URLs.
    project_urls={
        "Bug Reports": "https://github.com/philip-brohan/IRData/issues",
        "Source": "https://github.com/philip-brohan/IRData",
    },
)
