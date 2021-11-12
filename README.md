# Ewoks: ESRF Workflow System

Many [workflow management systems](https://s.apache.org/existing-workflow-systems) exist to deal with data processing problems that can be expressed as a graph of tasks, also referred to as a *computational graph* or *workflow*. The main purpose of a workflow management system is to provide a framework for implementing tasks, creating graphs of tasks and executing these graphs.

The purpose of *ewoks* is to provide an abstraction layer between graph representation and execution. This allows using the same tasks and graphs in different workflow management systems. *ewoks* itself is **not** a workflow management system.

## Install

```bash
python -m pip install ewoks[orange,dask,ppf,test]
```

## Test

```bash
pytest --pyargs ewoks.tests
```

## Getting started

Workflows can be loaded and executed from the command line

```bash
ewoks execute /path/to/graph.json [--scheduler dask]
```

or in a python script (using the core library or any of the bindings)

```python
from ewokscore import execute_graph
# from ewoksppf import execute_graph
# from ewoksdask import execute_graph
# from ewoksorange import execute_graph

result = execute_graph("/path/to/graph.json")
```

The core library `ewokscore` is used for loading graphs and can also be used for sequential execution.

## Documentation

https://workflow.gitlab-pages.esrf.fr/ewoks/ewoks
