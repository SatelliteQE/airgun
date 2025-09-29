"""Sphinx documentation generator configuration file.

The full set of configuration options is listed on the Sphinx website:
http://sphinx-doc.org/config.html

"""

import os
import sys


def skip_data(app, what, name, obj, skip, options):
    """Skip double generating docs for airgun.settings"""
    if what == "data" and name == "airgun.settings":
        return True
    return None


def setup(app):
    app.connect("autoapi-skip-member", skip_data)


# Add the AirGun root directory to the system path. This allows references
# such as :mod:`airgun.browser` to be processed correctly.
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)

# Project Information ---------------------------------------------------------

project = "AirGun"
copyright = "2018, Andrii Balakhtar"
version = "0.0.1"
release = version

# General Configuration -------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinxcontrib.spelling",
    "autoapi.extension",
]
autodoc_inherit_docstrings = False
autoapi_dirs = ["../airgun"]
autoapi_keep_files = True
autoapi_options = [
    "members",
    "undoc-members",
    "private-members",
    "imported-members",
    "show-module-summary",
    "special-members",
]
source_suffix = ".rst"
master_doc = "index"
exclude_patterns = ["_build"]

intersphinx_mapping = {
    "python": ("http://docs.python.org/3.6", None),
    # 'widgetastic':
    #   ('http://widgetasticcore.readthedocs.io/en/latest/', None),
    # 'navmazing': ('http://navmazing.readthedocs.io/en/latest/', None),
}
spelling_word_list_filename = "spelling_wordlist.txt"
spelling_show_suggestions = True
