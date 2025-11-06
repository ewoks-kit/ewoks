from ewokscore.graph import TaskGraph

from ..._requirements.metadata.parse import parse_requirements


def assert_in_graph_requirements(graph: TaskGraph, *distribution_names) -> None:
    assert distribution_names, "no names provides"
    assert "requirements" in graph.graph.graph, "no requirements"
    requirements = parse_requirements(graph.graph.graph["requirements"])

    existing = {distribution.name for distribution in requirements.distributions}
    not_existing = set(distribution_names) - existing
    assert not not_existing, f"{sorted(not_existing)} not in requirements"
