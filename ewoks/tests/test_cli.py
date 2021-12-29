import sys
import pytest

from ewoks.__main__ import main
from ewokscore import load_graph
from ewokscore.tests.examples.graphs import graph_names
from ewokscore.tests.examples.graphs import get_graph
from ewoksppf.tests.test_examples import assert_results as assert_ppf_results
from ewoksdask.tests.test_examples import assert_all_results as assert_dask_results
from ewokscore.tests.test_examples import assert_all_results as assert_core_results


@pytest.mark.parametrize("graph_name", graph_names())
@pytest.mark.parametrize("scheme", (None, "json"))
@pytest.mark.parametrize("binding", ("none", "dask", "ppf"))
def test_main_execute(graph_name, scheme, binding, tmpdir):
    if scheme == "json":
        pytest.skip("TODO")
    graph, expected = get_graph(graph_name)
    argv = [
        sys.executable,
        "execute",
        graph_name,
        "--test",
        "--binding",
        binding,
        "--output",
        "all",
    ]
    if scheme:
        argv += ["--root_uri", str(tmpdir), "scheme", scheme]
        varinfo = {"root_uri": str(tmpdir), "scheme": scheme}
    else:
        varinfo = None

    ewoksgraph = load_graph(graph)
    non_dag = ewoksgraph.is_cyclic or ewoksgraph.has_conditional_links

    if non_dag and binding != "ppf":
        with pytest.raises(RuntimeError):
            main(argv=argv, shell=False)
        return

    result = main(argv=argv, shell=False)

    if binding == "ppf":
        assert_ppf_results(graph, ewoksgraph, result, expected, varinfo)
    elif binding == "dask":
        assert_dask_results(ewoksgraph, result, expected, varinfo)
    else:
        assert_core_results(ewoksgraph, result, expected, varinfo)
