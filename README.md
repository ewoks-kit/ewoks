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

The core library is used to represent graphs and the bindings are used to execute them:

```bash
from ewokscore import load_graph
from ewoksppf import execute_graph

result = execute_graph(load_graph("/path/to/graph.json"))
```

## Documentation

https://workflow.gitlab-pages.esrf.fr/ewoks/ewoks
