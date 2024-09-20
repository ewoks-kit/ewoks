# Ewoks: Extensible Workflow System

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
