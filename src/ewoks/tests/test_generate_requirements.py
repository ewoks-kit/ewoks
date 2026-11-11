from ewoks import convert_graph
from ewoks import generate_requirements


def test_generate_requirements():
    requirements = generate_requirements(engine=("ewoksorange", "1.2.3"))
    assert requirements["ewoks"]["engine"] == {
        "name": "ewoksorange",
        "version": "1.2.3",
    }
    assert requirements["distributions"]


def test_generate_requirements_like_convert():
    graph = {"graph": {"id": "test"}, "nodes": [], "links": []}
    converted = convert_graph(graph, None, save_options={"representation": "json_dict"})
    requirements = generate_requirements()
    assert requirements.keys() == converted["graph"]["requirements"].keys()
