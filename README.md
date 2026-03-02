# Ewoks: Extensible Workflow System

[![Pipeline](https://github.com/ewoks-kit/ewoks/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/ewoks-kit/ewoks/actions/workflows/test.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/github/license/ewoks-kit/ewoks)](https://github.com/ewoks-kit/ewoks/blob/main/LICENSE.md)
[![Coverage](https://codecov.io/gh/ewoks-kit/ewoks/branch/main/graph/badge.svg)](https://codecov.io/gh/ewoks-kit/ewoks)
[![Docs](https://readthedocs.org/projects/ewoks/badge/?version=latest)](https://ewoks.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/ewoks)](https://pypi.org/project/ewoks/)

Many [workflow management systems](https://s.apache.org/existing-workflow-systems) exist to deal with data processing problems that can be expressed as a graph of tasks, also referred to as a *computational graph* or *workflow*. The main purpose of a workflow management system is to provide a framework for implementing tasks, creating graphs of tasks and executing these graphs.

The purpose of *ewoks* is to provide an abstraction layer between graph representation and execution. This allows using the same tasks and graphs in different workflow management systems. *ewoks* itself is **not** a workflow management system.

## Install

```bash
pip install ewoks[orange,dask,ppf,test]
```

## Test

```bash
pytest --pyargs ewoks.tests
```

## Getting started

Workflows can be executed from the command line

```bash
ewoks execute /path/to/graph.json [--engine dask]
```

or for an installation with the system python

```bash
python3 -m ewoks execute /path/to/graph.json [--engine dask]
```

Workflows can also be executed from python

```python
from ewoks import execute_graph

result = execute_graph("/path/to/graph.json", engine="dask")
```

When no engine is specified it will use sequential execution from `ewokscore`.

## Documentation

https://ewoks.readthedocs.io/
