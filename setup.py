import os
from setuptools import setup

__author__ = "Daren Thomas"
__copyright__ = "Copyright 2018, Architecture and Building Systems - ETH Zurich"
__credits__ = ["Daren Thomas"]
__license__ = "MIT"
__version__ = "0.0.1"
__maintainer__ = "Daren Thomas"
__email__ = "cea@arch.ethz.ch"
__status__ = "Production"

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="cea_dashboard",
    version=__version__,
    author="Daren Thomas",
    author_email='cea@arch.ethz.ch',
    description=("A dashboard interface for the CityEnergyAnalyst"),
    license="MIT",
    keywords="dashboard cea flask plotly",
    url='http://cityenergyanalyst.com',
    packages=['cea_dashboard'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Flask",
        "License :: OSI Approved :: MIT License",
    ],
)
