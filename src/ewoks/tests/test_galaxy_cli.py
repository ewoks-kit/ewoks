import sys

from ewoks.__main__ import main


def test_failure_galaxy_execution(capsys):
    main(
        argv=[
            sys.executable,
            "galaxy",
            "ewokscore.tests.examples.tasks.sumtask.SumTask",
        ],
        shell=False,
    )
    captured = capsys.readouterr()

    assert "FAILED" in captured.out
    assert "Missing inputs" in captured.err


def test_successful_galaxy_execution(capsys):
    main(
        argv=[
            sys.executable,
            "galaxy",
            "ewokscore.tests.examples.tasks.sumtask.SumTask",
            "-p",
            "a=2",
            "-p",
            "b=3",
        ],
        shell=False,
    )
    captured = capsys.readouterr()

    assert "FINISHED" in captured.out
    assert "RESULTS:\n{'result': 5}" in captured.out
    assert captured.err == ""
