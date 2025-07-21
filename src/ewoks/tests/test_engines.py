import pytest

from .._engines import get_engine_names
from .._engines import get_execution_engine
from .._engines import get_serialization_engine


def test_engine_name_discovery():
    names = get_engine_names()
    expected = {"core", "dask", "ppf", "orange"}
    assert expected.issubset(names)


def test_execution_engine_discovery():
    core_engine = get_execution_engine("core")
    for name in (None, "none", "None"):
        engine = get_execution_engine(name)
        assert engine.__class__ is core_engine.__class__

    for engine in ("ppf", "dask", "orange"):
        _ = get_execution_engine(engine)

    with pytest.raises(RuntimeError):
        _ = get_execution_engine("__wrong_value__")


def test_serialization_engine_discovery():
    orange_engine = get_execution_engine("orange")
    engine, representation = get_serialization_engine("test.ows")
    assert engine.__class__ is orange_engine.__class__
    assert representation == "ows"

    core_engine = get_execution_engine("core")
    engine, representation = get_serialization_engine("test.json")
    assert engine.__class__ is core_engine.__class__
    assert representation == "json"

    core_engine = get_execution_engine("core")
    engine, representation = get_serialization_engine("{}")
    assert engine.__class__ is core_engine.__class__
    assert representation == "json_string"
