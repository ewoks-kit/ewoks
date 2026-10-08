# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


import importlib.metadata
import os

release = importlib.metadata.version("ewoks")

project = "ewoks"
version = ".".join(release.split(".")[:2])
copyright = "2021-2026, ESRF"
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
    "sphinx_copybutton",
    "sphinx_tabs.tabs",
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

copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_title = docstitle
html_logo = "_static/logo.png"
html_static_path = ["_static"]
html_extra_path = ["../src/ewoks/_bootstrap"]
html_template_path = ["_templates"]
html_css_files = ["custom.css"]

html_theme_options = {
    "icon_links": [
        {
            "name": "github",
            "url": "https://github.com/ewoks-kit/ewoks",
            "icon": "fa-brands fa-github",
        },
        {
            "name": "pypi",
            "url": "https://pypi.org/project/ewoks",
            "icon": "fa-brands fa-python",
        },
        {
            "name": "matrix",
            "url": "https://matrix.to/#/#ewoks:helmholtz.cloud",
            "icon": "_static/matrix-icon.svg",
            "type": "local",
        },
    ],
    "logo": {
        "text": docstitle,
    },
    "footer_start": ["copyright"],
    "footer_end": ["footer_end"],
}

# Root of the documentation version that is built: on Read the Docs, for example
# .../en/stable, or on GitLab Pages
_DOCS_URL = (
    os.environ.get("READTHEDOCS_CANONICAL_URL")
    or os.environ.get("CI_PAGES_URL")
    or "https://ewoks.readthedocs.io/en/latest"
).rstrip("/")


def _substitute_docs_url(app, docname, source):
    # Substitutions are not supported in code blocks
    source[0] = source[0].replace("|docs_url|", _DOCS_URL)


def setup(app):
    app.connect("source-read", _substitute_docs_url)
