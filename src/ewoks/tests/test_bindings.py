import pytest

from ..bindings import import_binding


def test_import_binding():
    _ = import_binding()
    for engine in (None, "none", "core", "ppf", "dask", "orange"):
        _ = import_binding(engine)


def test_wrong_import_binding():
    with pytest.raises(ImportError, match="Cannot import binding for engine 'wrong'"):
        _ = import_binding("wrong")
