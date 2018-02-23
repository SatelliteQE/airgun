"""Sphinx documentation generator configuration file.

The full set of configuration options is listed on the Sphinx website:
http://sphinx-doc.org/config.html

"""
import sys
import os


# Add the AirGun root directory to the system path. This allows references
# such as :mod:`airgun.browser` to be processed correctly.
sys.path.insert(
    0,
    os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        os.path.pardir
    ))
)

# Project Information ---------------------------------------------------------

project = 'AirGun'
copyright = '2018, Andriy Balakhtar'
version = '0.0.1'
release = version

# General Configuration -------------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
]
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build']
nitpicky = True
