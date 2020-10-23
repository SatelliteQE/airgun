"""Sphinx documentation generator configuration file.

The full set of configuration options is listed on the Sphinx website:
http://sphinx-doc.org/config.html

"""
import os
import sys


def skip_data(app, what, name, obj, skip, options):
    """Skip double generating docs for airgun.settings"""
    if what == 'data' and name == 'airgun.settings':
        return True
    return None


def setup(app):
    app.connect("autoapi-skip-member", skip_data)


# Add the AirGun root directory to the system path. This allows references
# such as :mod:`airgun.browser` to be processed correctly.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

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
    'autoapi.extension',
]
autoapi_dirs = ['../airgun']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build']
nitpicky = True
nitpick_ignore = [
    ('py:class', 'navmazing.Navigate'),
    ('py:class', 'navmazing.NavigateStep'),
    ('py:class', 'widgetastic.browser.Browser'),
    ('py:class', 'widgetastic.browser.DefaultPlugin'),
    ('py:class', 'widgetastic.widget.Checkbox'),
    ('py:class', 'widgetastic.widget.ClickableMixin'),
    ('py:class', 'widgetastic.widget.GenericLocatorWidget'),
    ('py:class', 'widgetastic.widget.ParametrizedView'),
    ('py:class', 'widgetastic.widget.Select'),
    ('py:class', 'widgetastic.widget.Table'),
    ('py:class', 'widgetastic.widget.TableColumn'),
    ('py:class', 'widgetastic.widget.TableRow'),
    ('py:class', 'widgetastic.widget.Text'),
    ('py:class', 'widgetastic.widget.TextInput'),
    ('py:class', 'widgetastic.widget.View'),
    ('py:class', 'widgetastic.widget.Widget'),
    ('py:class', 'widgetastic.widget.WTMixin'),
    ('py:class', 'widgetastic_patternfly.AggregateStatusCard'),
    ('py:class', 'widgetastic_patternfly.Button'),
    ('py:class', 'widgetastic_patternfly.FlashMessage'),
    ('py:class', 'widgetastic_patternfly.FlashMessages'),
    ('py:class', 'widgetastic_patternfly.Tab'),
    ('py:class', 'widgetastic_patternfly.TabWithDropdown'),
    ('py:class', 'widgetastic_patternfly.VerticalNavigation'),
    ('py:meth', 'navmazing.NavigateStep.go'),
    ('py:meth', 'Widget.read'),
]
intersphinx_mapping = {
    'python': ('http://docs.python.org/3.6', None),
    # 'widgetastic':
    #   ('http://widgetasticcore.readthedocs.io/en/latest/', None),
    # 'navmazing': ('http://navmazing.readthedocs.io/en/latest/', None),
}
spelling_word_list_filename = 'spelling_wordlist.txt'
spelling_show_suggestions = True
