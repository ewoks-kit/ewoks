from contextlib import contextmanager
from typing import Any


def has_default_input(node: dict, input_name: str, value: Any) -> bool:
    for default_input in node["default_inputs"]:
        if default_input["name"] == input_name:
            return default_input["value"] == value
    else:
        return False


@contextmanager
def no_widget_registry():
    try:
        yield
    finally:
        from orangecontrib.ewoksnowidget import global_cleanup_ewoksnowidget

        global_cleanup_ewoksnowidget()
