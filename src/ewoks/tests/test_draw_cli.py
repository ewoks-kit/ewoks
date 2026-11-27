import sys

import pytest
from ewokscore.tests.examples.graphs import graph_names

from ewoks.__main__ import main

pytest.importorskip("ewoksdraw")


@pytest.mark.parametrize("graph_name", graph_names())
def test_draw(tmpdir, graph_name, capsys):
    destination = str(tmpdir / f"{graph_name}.svg")
    return_code = main(  # noqa: S604
        argv=[sys.executable, "draw", graph_name, destination, "--test"],
        shell=True,
    )

    assert return_code == 0
    with open(destination) as f:
        assert "<svg" in f.read()
    assert f"Drew {graph_name} -> {destination}" in capsys.readouterr().out
