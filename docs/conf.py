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
nitpick_ignore = [
    ('py:class', 'widgetastic.browser.Browser'),
    ('py:class', 'widgetastic.widget.View'),
    ('py:class', 'navmazing.Navigate'),
    ('py:class', 'navmazing.NavigateStep'),
    ('py:meth', 'navmazing.NavigateStep.go'),
    ('py:meth', 'current_org'),
    ('py:meth', 'current_loc'),
    ('py:meth', 'select'),
    ('py:meth', 'fill_with'),
    ('py:class', 'bool'),
    ('py:class', 'dict'),
    ('py:class', 'str'),
]
# FIXME: No idea why I need these in the ignore list above (looks good to
# my eyes in the code):
#    ('py:meth', 'current_org'),
#    ('py:meth', 'current_loc'),
#    ('py:meth', 'select'),
#    ('py:meth', 'fill_with'),
