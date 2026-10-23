import os
import subprocess
import sys

import pytest

from ewoks.__main__ import main

from .utils import no_widget_registry


def test_show(capsys, monkeypatch):
    monkeypatch.setenv("LC_ALL", "C.UTF-8")

    argv = [sys.executable, "show", "demo", "--test"]
    main(argv=argv, shell=False)
    captured = capsys.readouterr()

    expected = """
Workflow: demo
Id: demo
Description: demo
╒════════╤════════════════╤═══════════════════╤═══════╕
│ Name   │ Value          │ Task identifier   │ Id    │
╞════════╪════════════════╪═══════════════════╪═══════╡
│ list   │ [0, 1, 2]      │ SumList           │ task0 │
├────────┼────────────────┼───────────────────┼───────┤
│ delay  │ 0              │ SumList           │ task0 │
├────────┼────────────────┼───────────────────┼───────┤
│ b      │ <MISSING_DATA> │ SumTask           │ task1 │
├────────┼────────────────┼───────────────────┼───────┤
│ delay  │ 0              │ SumTask           │ task1 │
├────────┼────────────────┼───────────────────┼───────┤
│ a      │ 2              │ SumTask           │ task2 │
├────────┼────────────────┼───────────────────┼───────┤
│ b      │ <MISSING_DATA> │ SumTask           │ task2 │
├────────┼────────────────┼───────────────────┼───────┤
│ delay  │ 0              │ SumTask           │ task2 │
├────────┼────────────────┼───────────────────┼───────┤
│ b      │ 3              │ SumTask           │ task3 │
├────────┼────────────────┼───────────────────┼───────┤
│ delay  │ 0              │ SumTask           │ task3 │
├────────┼────────────────┼───────────────────┼───────┤
│ b      │ 4              │ SumTask           │ task4 │
├────────┼────────────────┼───────────────────┼───────┤
│ delay  │ 0              │ SumTask           │ task4 │
├────────┼────────────────┼───────────────────┼───────┤
│ delay  │ 0              │ SumTask           │ task5 │
├────────┼────────────────┼───────────────────┼───────┤
│ b      │ 6              │ SumTask           │ task6 │
├────────┼────────────────┼───────────────────┼───────┤
│ delay  │ 0              │ SumTask           │ task6 │
╘════════╧════════════════╧═══════════════════╧═══════╛
"""
    assert captured.out == expected
    assert captured.err == ""


@pytest.mark.parametrize(
    "env_override",
    [
        {"PYTHONIOENCODING": "ascii"},
        {"LC_ALL": "POSIX"},
        {"LC_ALL": None, "LC_CTYPE": None, "LANG": None},
    ],
)
def test_show_ascii_stdout(env_override):
    env = {**os.environ, **env_override}
    env = {k: v for k, v in env.items() if v is not None}
    argv = [sys.executable, "-m", "ewoks", "show", "demo", "--test"]
    result = subprocess.run(  # noqa: S603 - Trusted test command
        argv, env=env, capture_output=True, text=True
    )

    expected = """
Workflow: demo
Id: demo
Description: demo
+--------+----------------+-------------------+-------+
| Name   | Value          | Task identifier   | Id    |
+========+================+===================+=======+
| list   | [0, 1, 2]      | SumList           | task0 |
+--------+----------------+-------------------+-------+
| delay  | 0              | SumList           | task0 |
+--------+----------------+-------------------+-------+
| b      | <MISSING_DATA> | SumTask           | task1 |
+--------+----------------+-------------------+-------+
| delay  | 0              | SumTask           | task1 |
+--------+----------------+-------------------+-------+
| a      | 2              | SumTask           | task2 |
+--------+----------------+-------------------+-------+
| b      | <MISSING_DATA> | SumTask           | task2 |
+--------+----------------+-------------------+-------+
| delay  | 0              | SumTask           | task2 |
+--------+----------------+-------------------+-------+
| b      | 3              | SumTask           | task3 |
+--------+----------------+-------------------+-------+
| delay  | 0              | SumTask           | task3 |
+--------+----------------+-------------------+-------+
| b      | 4              | SumTask           | task4 |
+--------+----------------+-------------------+-------+
| delay  | 0              | SumTask           | task4 |
+--------+----------------+-------------------+-------+
| delay  | 0              | SumTask           | task5 |
+--------+----------------+-------------------+-------+
| b      | 6              | SumTask           | task6 |
+--------+----------------+-------------------+-------+
| delay  | 0              | SumTask           | task6 |
+--------+----------------+-------------------+-------+
"""
    assert result.stdout == expected
    assert result.stderr == ""


def test_show_with_inputs(capsys, monkeypatch):
    monkeypatch.setenv("LC_ALL", "C.UTF-8")

    argv = [sys.executable, "show", "demo", "--test", "-pa", "b=999"]
    main(argv=argv, shell=False)
    captured = capsys.readouterr()

    expected = """
Workflow: demo
Id: demo
Description: demo
╒════════╤═══════════╤═══════════════════╤═══════╕
│ Name   │ Value     │ Task identifier   │ Id    │
╞════════╪═══════════╪═══════════════════╪═══════╡
│ list   │ [0, 1, 2] │ SumList           │ task0 │
├────────┼───────────┼───────────────────┼───────┤
│ delay  │ 0         │ SumList           │ task0 │
├────────┼───────────┼───────────────────┼───────┤
│ b      │ 999       │ SumTask           │ task1 │
├────────┼───────────┼───────────────────┼───────┤
│ delay  │ 0         │ SumTask           │ task1 │
├────────┼───────────┼───────────────────┼───────┤
│ a      │ 2         │ SumTask           │ task2 │
├────────┼───────────┼───────────────────┼───────┤
│ b      │ 999       │ SumTask           │ task2 │
├────────┼───────────┼───────────────────┼───────┤
│ delay  │ 0         │ SumTask           │ task2 │
├────────┼───────────┼───────────────────┼───────┤
│ b      │ 999       │ SumTask           │ task3 │
├────────┼───────────┼───────────────────┼───────┤
│ delay  │ 0         │ SumTask           │ task3 │
├────────┼───────────┼───────────────────┼───────┤
│ b      │ 999       │ SumTask           │ task4 │
├────────┼───────────┼───────────────────┼───────┤
│ delay  │ 0         │ SumTask           │ task4 │
├────────┼───────────┼───────────────────┼───────┤
│ delay  │ 0         │ SumTask           │ task5 │
├────────┼───────────┼───────────────────┼───────┤
│ b      │ 999       │ SumTask           │ task6 │
├────────┼───────────┼───────────────────┼───────┤
│ delay  │ 0         │ SumTask           │ task6 │
╘════════╧═══════════╧═══════════════════╧═══════╛
"""
    assert captured.out == expected
    assert captured.err == ""


def test_show_with_convert_ows(capsys, tmpdir, monkeypatch):
    monkeypatch.setenv("LC_ALL", "C.UTF-8")

    # Generate an OWS file
    graph_name = "demo"
    destination = str(tmpdir / f"{graph_name}.ows")
    argv = [
        sys.executable,
        "convert",
        graph_name,
        destination,
        "--test",
    ]
    with no_widget_registry():
        main(argv=argv, shell=False)
    assert os.path.exists(destination)
    capsys.readouterr()

    # Show the OWS file
    argv = [sys.executable, "show", destination]
    main(argv=argv, shell=False)
    captured = capsys.readouterr()

    expected = f"""
Workflow: {destination}
Id: demo
Description: demo
╒════════╤════════════════╤═══════════════════╤═══════╤═════════╕
│ Name   │ Value          │ Task identifier   │ Id    │ Label   │
╞════════╪════════════════╪═══════════════════╪═══════╪═════════╡
│ list   │ [0, 1, 2]      │ SumList           │ task0 │ task0   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ delay  │ 0              │ SumList           │ task0 │ task0   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ b      │ <MISSING_DATA> │ SumTask           │ task1 │ task1   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ delay  │ 0              │ SumTask           │ task1 │ task1   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ a      │ 2              │ SumTask           │ task2 │ task2   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ b      │ <MISSING_DATA> │ SumTask           │ task2 │ task2   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ delay  │ 0              │ SumTask           │ task2 │ task2   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ b      │ 3              │ SumTask           │ task3 │ task3   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ delay  │ 0              │ SumTask           │ task3 │ task3   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ b      │ 4              │ SumTask           │ task4 │ task4   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ delay  │ 0              │ SumTask           │ task4 │ task4   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ delay  │ 0              │ SumTask           │ task5 │ task5   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ b      │ 6              │ SumTask           │ task6 │ task6   │
├────────┼────────────────┼───────────────────┼───────┼─────────┤
│ delay  │ 0              │ SumTask           │ task6 │ task6   │
╘════════╧════════════════╧═══════════════════╧═══════╧═════════╛
"""
    assert captured.out == expected
    assert captured.err == ""
