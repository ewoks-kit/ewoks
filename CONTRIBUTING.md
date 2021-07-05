## Getting started

Requirements are listed in `setup.cfg` and can be installed with

```bash
pip install [--user] .[dev]
```

## Linting

The configuration for [black](https://black.readthedocs.io/en/stable/) and [flake8](https://flake8.pycqa.org/en/latest/index.html) can be modified in `setup.cfg`.

Comment lines with `# noqa: E123` to ignore certain linting errors.

## Testing

Tests make use [pytest](https://docs.pytest.org/en/stable/index.html) and can be run as follows

```bash
pytest .
```

## Releasing
1. Add the [changes](https://changelog.md) to `CHANGELOG.md`
2. Increment the version number in `<project>/__init__.py`. The number must match the  [regex pattern](https://regex101.com/r/Ly7O1x/3/) provided by the [semantic versioning](https://semver.org) guidelines. For example the lifecycle of a single version could be
   ```
   1.0.0-alpha < 1.0.0-alpha.1 < 1.0.0-beta < 1.0.0-beta.1 < 1.0.0-rc.1 < 1.0.0
   ```
3. Create a git tag and write release notes in the `Tags` page of the gitlab repository
   ```bash
   git tag v1.2.3 -m "Release version 1.2.3"
   git push && git push --tags
   ```
4. Deploy on [pypitest](https://test.pypi.org) and [pypi](https://pypi.org)
   ```bash
   python setup.py sdist
   twine upload -r pypitest --sign dist/*
   twine upload -r pypi --sign dist/*
   ```
