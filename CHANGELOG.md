# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [4.0.1] - 2026-03-02

### Changed

- Project migrated to https://github.com/ewoks-kit/ewoks.

## [4.0.0] - 2025-12-30

### Changes

- Depend on `ewokscore 4.x`.

## [3.0.0] - 2025-12-12

### Added

- `execute_graph`: ICAT startDate and endDate are the start and end of the workflow by default.

### Changes

- Depend on `ewoksorange 3.x`.

## [2.1.2] - 2025-11-07

### Fixed

- Handle failure of requirement generation when `pip` is not installed.

## [2.1.1] - 2025-11-03

### Fixed

- Improved "requires package" error messages.

## [2.1.0] - 2025-10-31

### Added

- Add `ewoks cancel` CLI command.

### Changed

- CLI: refactor and rename modules.

## [2.0.1] - 2025-08-15

### Fixed

- Try the `core` engine first when (de)serializing graphs.

## [2.0.0] - 2025-07-25

### Added

- Use `ewoks.engines` entry points to find engines by name.
- Use `ewoks.engines.serialization.representations` entry points to find engines by graph representation.

## [1.3.0] - 2025-06-26

### Added

- Ewoks CLI `install` command: sanitize requirements, especially handling editable installations without a remote.

## [1.2.0] - 2025-06-12

### Added

- Ewoks CLI `show` command: print all workflow parameters that are not connected to outputs from other nodes.

## [1.1.0] - 2025-04-07

### Added

- The base class to create Ewoks tasks can be imported from `ewoks`: `from ewoks import Task`.
- `submit_graph` can be imported from `ewoks`: `from ewoks import submit_graph`.
- Task inputs can be defined via a Pydantic model (`input_model`) instead of `input_names`, `optional_input_names`.
  The model needs to derive from `BaseInputModel`: `from ewoks import BaseInputModel`.

### Changed

- Drop Python 3.6 and 3.7 and add support for Python 3.13.

## [1.0.0] - 2024-12-25

### Changed

- Remove deprecated argument `binding` from `execute_graph`.

## [0.6.0] - 2024-11-08

### Added

- Add graph installation to the python API (`install_graph`) and CLI (`ewoks install`).
- Add requirements when converting a graph so the graph becomes installable. This is an opt-out feature.
- Add task options to python API (`execute_graph` and `submit_graph`) and CLI (`ewoks install` and `ewoks submit`).

## [0.5.0] - 2024-06-23

### Changed

- Client-side graph resolution by default for submitting workflows.

### Fixed

- The pyyaml 6.0.2rc1 package is broken.

## [0.4.3] - 2024-02-13

### Changed

- Ewoks CLI workflow search: sort by creation date.
- Ewoks CLI `convert` command: support multiple workflow arguments.

## [0.4.2] - 2024-02-05

### Added

- CLI support for multiple workflows (explicit or with search pattern).

## [0.4.1] - 2023-12-15

### Added

- Improved documentation.

### Fixed

- Fix test dependencies.

## [0.4.0] - 2023-12-15

### Added

- Add support for jupyter notebooks as workflow tasks.

## [0.3.0] - 2023-06-09

### Changed

- Update dependency bounds.

## [0.2.0] - 2023-03-27

### Changed

- CLI: rename --output to --outputs.
- Add celery options to `submit_graph` and `ewoks submit`.

## [0.1.5] - 2023-03-23

### Changed

- Add 'esrf-data-portal' as extra pip requirement.

## [0.1.4] - 2023-03-23

### Added

- Add saving and uploading to graph execution.

## [0.1.3] - 2023-03-20

### Added

- Workflow caching when loading.

### Fixed

- CLI binding argument no longer exists for `ewoks submit`.

## [0.1.2] - 2023-03-09

### Deprecated

- Ewoks event field "binding" is deprecated in favor of "engine".

## [0.1.1] - 2023-03-08

### Changed

- Pin minor versions of ewoks projects.

## [0.1.0] - 2023-01-11

### Added

- `ewokscore` dependency.
- `ewoksdask` dependency.
- `ewoksorange` dependency.
- `ewoksppf` dependency.
- Command-line interface.

[unreleased]: https://github.com/ewoks-kit/ewoks/compare/v4.0.0...HEAD
[4.0.0]: https://github.com/ewoks-kit/ewoks/compare/v3.0.0...v4.0.0
[3.0.0]: https://github.com/ewoks-kit/ewoks/compare/v2.1.2...v3.0.0
[2.1.2]: https://github.com/ewoks-kit/ewoks/compare/v2.1.1...v2.1.2
[2.1.1]: https://github.com/ewoks-kit/ewoks/compare/v2.1.0...v2.1.1
[2.1.0]: https://github.com/ewoks-kit/ewoks/compare/v2.0.1...v2.1.0
[2.0.1]: https://github.com/ewoks-kit/ewoks/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/ewoks-kit/ewoks/compare/v1.3.0...v2.0.0
[1.3.0]: https://github.com/ewoks-kit/ewoks/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/ewoks-kit/ewoks/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/ewoks-kit/ewoks/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/ewoks-kit/ewoks/compare/v0.6.0...v1.0.0
[0.6.0]: https://github.com/ewoks-kit/ewoks/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/ewoks-kit/ewoks/compare/v0.4.3...v0.5.0
[0.4.3]: https://github.com/ewoks-kit/ewoks/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/ewoks-kit/ewoks/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/ewoks-kit/ewoks/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/ewoks-kit/ewoks/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ewoks-kit/ewoks/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ewoks-kit/ewoks/compare/v0.1.5...v0.2.0
[0.1.5]: https://github.com/ewoks-kit/ewoks/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/ewoks-kit/ewoks/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/ewoks-kit/ewoks/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/ewoks-kit/ewoks/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/ewoks-kit/ewoks/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ewoks-kit/ewoks/-/tags/v0.1.0
