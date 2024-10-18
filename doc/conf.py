"""rm -rf doc/_generated/; sphinx-build doc build/sphinx/html -E -a
"""

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

from ewoks import __version__ as release

project = "ewoks"
version = ".".join(release.split(".")[:2])
copyright = "2021-present, ESRF"
author = "ESRF"
docstitle = f"{project} {version}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinxarg.ext",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "nbsphinx",
    "nbsphinx_link",
]
templates_path = ["_templates"]
exclude_patterns = ["build", "**.ipynb_checkpoints"]

always_document_param_types = True


autosummary_generate = True
autodoc_default_flags = [
    "members",
    "undoc-members",
    "show-inheritance",
]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = []
html_theme_options = {
    "icon_links": [
        {
            "name": "gitlab",
            "url": "https://gitlab.esrf.fr/workflow/ewoks/ewoks",
            "icon": "fa-brands fa-gitlab",
        },
        {
            "name": "pypi",
            "url": "https://pypi.org/project/ewoks",
            "icon": "fa-brands fa-python",
        },
    ],
    "footer_start": ["copyright"],
    "footer_end": ["footer_end"],
}
