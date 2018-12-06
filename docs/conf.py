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
copyright = '2018, Andrii Balakhtar'
version = '0.0.1'
release = version

# General Configuration -------------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinxcontrib.spelling',
]
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build']
nitpicky = True
nitpick_ignore = [
    ('py:class', 'widgetastic.browser.Browser'),
    ('py:class', 'widgetastic.widget.Table'),
    ('py:class', 'widgetastic.widget.View'),
    ('py:class', 'navmazing.Navigate'),
    ('py:class', 'navmazing.NavigateStep'),
    ('py:class', 'airgun.views.common.BaseLoggedInView'),
    ('py:meth', 'widgetastic.browser.Browser.move_to_element'),
    ('py:meth', 'airgun.views.common.BaseLoggedInView.read'),
    ('py:meth', 'navmazing.NavigateStep.go'),
    ('py:meth', 'current_org'),
    ('py:meth', 'current_loc'),
    ('py:meth', 'select'),
    ('py:meth', 'fill_with'),
    ('py:meth', 'Widget.is_displayed'),
    ('py:obj', 'widgetastic.widget.View')
]
# FIXME: No idea why I need these in the ignore list above (looks good to
# my eyes in the code):
#    ('py:meth', 'current_org'),
#    ('py:meth', 'current_loc'),
#    ('py:meth', 'select'),
#    ('py:meth', 'fill_with'),
intersphinx_mapping = {
    'python': ('http://docs.python.org/3.6', None),
    # 'widgetastic':
    #   ('http://widgetasticcore.readthedocs.io/en/latest/', None),
    # 'navmazing': ('http://navmazing.readthedocs.io/en/latest/', None),
}
spelling_word_list_filename = 'spelling_wordlist.txt'
spelling_show_suggestions = True
