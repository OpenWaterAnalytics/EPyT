# -- Path setup --------------------------------------------------------------

import sys
import os

# Project root (so 'epyt' is importable as a package)
sys.path.insert(0, os.path.abspath('..'))

# epyt/src/ so modules inside src are discoverable by autodoc
sys.path.insert(0, os.path.abspath('../epyt/src'))

# -- Project information -----------------------------------------------------

project = 'epyt'
copyright = '2022, KIOS Research and Innovation Center of Excellence'
author = 'KIOS CoE'

# The full version, including alpha/beta/rc tags
release = '1.0.7'

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.duration',
    'sphinx.ext.doctest',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx_copybutton'
]

# Mock C extensions that cannot be imported during doc builds
autodoc_mock_imports = ['cffi']

# Autodoc settings - automatically document all members
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'member-order': 'bysource',
    'special-members': '__init__',
}

autosummary_generate = True

templates_path = ['_templates']

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
