"""rm -rf doc/_generated/; python setup.py build_sphinx -E -a
"""

project = "ewoks"
release = "0.1"
copyright = "2021, ESRF"
author = "ESRF"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "nbsphinx",
    "nbsphinx_link",
]
templates_path = ["_templates"]
exclude_patterns = ["build", "**.ipynb_checkpoints"]

pygments_style = "sphinx"
autodoc_typehints = "description"
autodoc_typehints_description_target = "all"

html_theme = "classic"
html_static_path = []

autosummary_generate = True
autodoc_default_flags = [
    "members",
    "undoc-members",
    "show-inheritance",
]
