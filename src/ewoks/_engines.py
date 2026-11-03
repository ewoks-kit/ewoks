import importlib.metadata
import logging
from functools import lru_cache
from typing import Any
from typing import Callable
from typing import Generator
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type

from ewokscore.engine_interface import WorkflowEngine
from ewokscore.engine_interface import WorkflowEngineWithSerialization
from ewokscore.entry_points import EntryPoint
from ewokscore.entry_points import entry_points

_logger = logging.getLogger(__name__)


@lru_cache(1)
def get_engine_names() -> List[str]:
    return [name for name, _ in _iter_engine_class_loaders_with_name()]


@lru_cache(1)
def get_graph_representations() -> List[str]:
    return [
        representation
        for representation, _ in _iter_engine_class_loaders_with_representation()
    ]


def get_execution_engine(engine_name: Optional[str]) -> WorkflowEngine:
    if not engine_name or engine_name.lower() == "none":
        engine_name = "core"

    for name, load_engine_cls in _iter_engine_class_loaders_with_name():
        if name == engine_name:
            try:
                engine_cls = load_engine_cls()
            except Exception as e:
                _logger.warning(
                    f"Unable to properly load '{name}' engine. Error is {e}"
                )
                continue
            else:
                return engine_cls()

    raise RuntimeError(f"No engine found for graph execution: '{engine_name}'")


def get_serialization_engine(
    graph: Any, representation: Optional[str] = None
) -> Tuple[WorkflowEngineWithSerialization, Optional[str]]:
    core_representation = representation
    if representation:
        for (
            representations,
            load_engine_cls,
        ) in _iter_engine_class_loaders_with_representation():
            if representation in representations:
                engine_cls = load_engine_cls()
                if not issubclass(engine_cls, WorkflowEngineWithSerialization):
                    continue
                return engine_cls(), representation
    else:
        for name, load_engine_cls in _iter_engine_class_loaders_with_name():
            try:
                engine_cls = load_engine_cls()
            except Exception as e:
                _logger.warning(
                    f"Unable to properly load serialization engine '{name}'. Error is {e}"
                )
                continue

            if not issubclass(engine_cls, WorkflowEngineWithSerialization):
                continue

            engine = engine_cls()
            representation = engine.get_graph_representation(graph)
            if representation:
                return engine, representation

    engine = get_execution_engine("core")
    if not isinstance(engine, WorkflowEngineWithSerialization):
        raise RuntimeError("The 'core' engine does not support graph serialization")
    return engine, core_representation


def get_engine_distribution(engine: WorkflowEngine) -> Optional[Tuple[str, str]]:
    """Name and version of the distribution that provides the engine."""
    module = type(engine).__module__
    for distribution in importlib.metadata.distributions():
        for entry_point in distribution.entry_points:
            if (
                entry_point.group == "ewoks.engines"
                and entry_point.value.split(":")[0] == module
            ):
                return distribution.metadata["Name"], distribution.version
    return None


_EngineClassLoaderGenerator = Generator[
    Tuple[str, Callable[[], Type[WorkflowEngine]]], None, None
]


def _iter_engine_class_loaders_with_name() -> _EngineClassLoaderGenerator:
    try:
        eps = entry_points(group="ewoks.engines")
    except Exception:
        return

    eps = sorted(eps, key=_sort_ewoks_engines)
    for ep in eps:
        yield ep.name, ep.load


def _iter_engine_class_loaders_with_representation() -> _EngineClassLoaderGenerator:
    try:
        eps = entry_points(group="ewoks.engines.serialization.representations")
    except Exception:
        return

    eps = sorted(eps, key=_sort_ewoks_engines)
    for ep in eps:
        yield ep.name, ep.load


def _sort_ewoks_engines(item: EntryPoint):
    return (item.name != "core", item)
