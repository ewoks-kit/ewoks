# CHANGELOG.md

## Unreleased

New features:

- Use `ewoks.engines` entry points to find engines by name.
- Use `ewoks.engines.serialization.representations` entry points to find engines by graph representation.

## 1.3.0

New features:

- Ewoks CLI `install` command: sanitize requirements, especially handling editable installations without a remote.

## 1.2.0

New features:

- Ewoks CLI `show` command: print all workflow parameters that are not connected to outputs from other nodes.

## 1.1.0

Changes:

- Drop Python 3.6 and 3.7 and add support for Python 3.13

New features:

- The base class to create Ewoks tasks can be imported from `ewoks`: `from ewoks import Task`.
- `submit_graph` can be imported from `ewoks`: `from ewoks import submit_graph`
- Task inputs can be defined via a Pydantic model (`input_model`) instead of `input_names`, `optional_input_names`. The model needs to derive from `BaseInputModel`: `from ewoks import BaseInputModel`.

## 1.0.0

Breaking changes:

- Remove deprecated argument `binding` from `execute_graph`.

## 0.6.0

New features:

- Add graph installation to the python API (`install_graph`) and CLI (`ewoks install`).
- Add requirements when converting a graph so the graph becomes installable. This is an opt-out feature.
- Add task options to python API (`execute_graph` and `submit_graph`) and CLI (`ewoks install` and `ewoks submit`).

## 0.5.0

Changes:

- Client-side graph resolution by default for submitting workflows.

Bug fixes:

- The pyyaml 6.0.2rc1 package is broken.

## 0.4.3

Changes:

- Ewoks CLI workflow search: sort by creation date.
- Ewoks CLI `convert` command: support multiple workflow arguments.

## 0.4.2

New features:

- CLI support for multiple workflows (explicit or with search pattern)

## 0.4.1

New features:

- Improved documentation

Bug fixes:

- Fix test dependencies

## 0.4.0

New features:

- add support for jupyter notebooks as workflow tasks

## 0.3.0

Changes:

- update dependency bounds

## 0.2.0

Breaking Changes:

- CLI: rename --output to --outputs

Changes:

- add celery options to `submit_graph` and `ewoks submit`

## 0.1.5

Changes:

- add 'esrf-data-portal' as extra pip requirement

## 0.1.4

New features:

- add saving and uploading to graph execution

## 0.1.3

New features:

- workflow caching when loading

Bug fixes:

- CLI binding argument no longer exists for `ewoks submit`

## 0.1.2

Deprecations:

- ewoks event field "binding" is deprecated in favor of "engine"

## 0.1.1

Changes:

- Pin minor versions of ewoks projects

## 0.1.0

New features:

- `ewokscore` dependency
- `ewoksdask` dependency
- `ewoksorange` dependency
- `ewoksppf` dependency
- command-line interface
