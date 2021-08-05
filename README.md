# Ewoks: ESRF Workflow System

This is a container project that allow installing the core library and optionally bindings for Workflow Management Systems.

## Install

```bash
python -m pip install ewoks[orange,dask,ppf,test]
```

## Test

```bash
pytest --pyargs ewoks.tests
```

## Getting started

The core library is used to represent graphs and the bindings are used to execute them:

```bash
from ewokscore import load_graph
from ewoksppf import execute_graph

result = execute_graph(load_graph("/path/to/graph.json"))
```

## Documentation

https://workflow.gitlab-pages.esrf.fr/ewoks/ewoks
