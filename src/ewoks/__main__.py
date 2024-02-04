import sys
import argparse
from typing import Optional

from pprint import pformat
from . import cliutils
from .bindings import execute_graph
from .bindings import convert_graph
from .bindings import submit_graph


def create_argument_parser(shell=False):
    parser = argparse.ArgumentParser(
        description="Esrf WOrKflow System CLI",
        prog="ewoks",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(help="Commands", dest="command")
    execute = subparsers.add_parser(
        "execute",
        help="Execute a workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    submit = subparsers.add_parser(
        "submit",
        help="Schedule a workflow execution",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    convert = subparsers.add_parser(
        "convert",
        help="Convert a workflow",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    cliutils.add_execute_parameters(execute, shell=shell)
    cliutils.add_submit_parameters(submit, shell=shell)
    cliutils.add_convert_parameters(convert, shell=shell)
    return parser


def command_execute(args, shell=False):
    cliutils.apply_execute_parameters(args, shell=shell)
    results = execute_graph(args.graph, engine=args.engine, **args.execute_options)
    _print_results(args, results)

    if shell:
        if results is None:
            return 1
        return 0
    return results


def command_submit(args, shell=False):
    cliutils.apply_submit_parameters(args, shell=shell)
    future = submit_graph(
        args.graph,
        engine=args.engine,
        **args.execute_options,
        _celery_options=args.cparameters,
    )
    print(f"Job submitted (ID: {future.task_id})")
    if args.wait >= 0:
        print("Waiting for results ...")
        try:
            results = future.get(timeout=args.wait)
        except Exception as e:
            if not _is_timeout(e):
                raise
            print(f"Workflow not finished after {args.wait}s")
        else:
            if args.outputs == "none":
                print("Workflow finished")
            else:
                _print_results(args, results)


def _print_results(args, results):
    if args.outputs == "none":
        return
    print(f"Result of workflow '{args.workflow}':\n{pformat(results)}")


def _is_timeout(exception: Optional[Exception]) -> bool:
    if exception is None:
        return False
    if isinstance(exception, TimeoutError):
        return True
    if _is_timeout(exception.__cause__):
        return True
    if _is_timeout(exception.__context__):
        return True
    return False


def command_convert(args, shell=False):
    cliutils.apply_convert_parameters(args, shell=shell)
    convert_graph(args.graph, args.destination, **args.convert_options)


def command_default(args, shell=False):
    if shell:
        return 0
    return None


def main(argv=None, shell=True):
    parser = create_argument_parser(shell=shell)

    if argv is None:
        argv = sys.argv
    args = parser.parse_args(argv[1:])

    if args.command == "execute":
        return command_execute(args, shell=shell)
    elif args.command == "submit":
        return command_submit(args, shell=shell)
    elif args.command == "convert":
        return command_convert(args, shell=shell)
    else:
        parser.print_help()
        return command_default(args, shell=shell)


if __name__ == "__main__":
    sys.exit(main())
