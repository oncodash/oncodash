# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'oncodash-app'
copyright = '2022, decider'
author = 'decider'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_js',
]
js_language = 'typescript'
js_source_path = '../../../src'

primary_domain = 'js'
jsdoc_config_path = '../../../tsconfig.json'

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

needs_sphinx = '4.0.2'
source_suffix = '.rst'  # ['.rst', '.md']
root_doc = 'index'

github_user = 'oncodash'
github_repo = 'oncodash'
github_version = 'main'

github_url = f'https://github.com/{github_user}/{github_repo}/'
gh_page_url = f'https://{github_user}.github.io/{github_repo}/'

html_context = {
    'display_github': True,
    'github_user': github_user,
    'github_repo': github_repo,
    'github_version': github_version,
    "conf_py_path": "/oncodash-app/docs/sphinx-js/source/",  # Path in the checkout to the docs root
}

html_baseurl = github_url
html_theme_options = {
    'github_url': github_url,

    'doc_items': {
        'Back-end': '/oncodash/backend',
        'Front-end': '/oncodash/frontend',
    },

    'home_url': 'https://oncodash.github.io/oncodash/',

    'logo': 'images/logo/logo.svg',
    'logo_dark': 'images/logo/oncodash-logo.svg',
    'logo_icon': 'images/logo/logo-icon.svg',
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'
html_theme = "trojanzoo_sphinx_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

def setup(app):
    app.add_css_file('css/oncodash.css')  # may also be an URL

html_favicon = 'images/favicon.ico'

# Allow numbering of figures/references.
numfig = True
