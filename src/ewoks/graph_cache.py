from collections import OrderedDict
from functools import wraps
from typing import Dict
from typing import Optional

from ewokscore.graph import TaskGraph
from ewokscore.hashing import uhash

_GRAPH_CACHE: Dict[int, TaskGraph] = OrderedDict()
_GRAPH_CACHE_MAX_SIZE: int = 0


def cache(load_method):
    @wraps(wraps)
    def wrapper(*args, graph_cache_max_size: Optional[int] = None, **kw):
        set_cache_max_size(graph_cache_max_size)

        if _GRAPH_CACHE_MAX_SIZE <= 0:
            return load_method(*args, **kw)

        graph_id = uhash((args, kw))
        graph = _GRAPH_CACHE.pop(graph_id, None)
        if graph is None:
            graph = load_method(*args, **kw)
        _GRAPH_CACHE[graph_id] = graph
        _check_cache_size()
        return graph

    return wrapper


def set_cache_max_size(graph_cache_max_size: Optional[int] = None) -> None:
    global _GRAPH_CACHE_MAX_SIZE
    if graph_cache_max_size is not None:
        _GRAPH_CACHE_MAX_SIZE = graph_cache_max_size
        _check_cache_size()


def _check_cache_size() -> None:
    while _GRAPH_CACHE and len(_GRAPH_CACHE) > _GRAPH_CACHE_MAX_SIZE:
        _GRAPH_CACHE.popitem(last=False)
