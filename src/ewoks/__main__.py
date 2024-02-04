import sys
import argparse
import traceback
from typing import Optional

from pprint import pprint
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

    return_code = 0
    keep_results = []
    for workflow, graph in zip(args.workflows, args.graphs):
        print("###################################")
        print(f"# Execute workflow '{workflow}'")
        print("###################################")
        try:
            results = execute_graph(graph, engine=args.engine, **args.execute_options)
        except Exception as ex:
            traceback.print_exc()
            print("FAILED")
            results = ex
            return_code = 1
        else:
            if args.outputs == "none":
                if results is None:
                    print("FAILED")
                else:
                    print("FINISHED")
            else:
                pprint(results)
                print("FINISHED")
            if results is None:
                return_code = 1
        finally:
            print()
        if not shell:
            keep_results.append(results)

    if shell:
        return return_code
    return keep_results


def command_submit(args, shell=False):
    cliutils.apply_submit_parameters(args, shell=shell)

    return_code = 0
    keep_results = []

    futures = list()
    for workflow, graph in zip(args.workflows, args.graphs):
        future = submit_graph(
            graph,
            engine=args.engine,
            **args.execute_options,
            _celery_options=args.cparameters,
        )
        print(f"Workflow '{workflow}' submitted (ID: {future.task_id})")
        futures.append(future)
    if args.wait < 0:
        if shell:
            return return_code
        return keep_results

    print("Waiting for results ...")
    print()
    for workflow, future in zip(args.workflows, futures):
        print(
            "###########################################################################"
        )
        print(f"# Result of workflow '{workflow}' (ID: {future.task_id})")
        print(
            "###########################################################################"
        )
        try:
            results = future.get(timeout=args.wait)
        except Exception as ex:
            if _is_timeout(ex):
                print(f"Not finished after {args.wait}s")
            else:
                traceback.print_exc()
                print("FAILED")
            results = ex
            return_code = 1
        else:
            if args.outputs == "none":
                if results is None:
                    print("FAILED")
                else:
                    print("FINISHED")
            else:
                pprint(results)
                print("FINISHED")
            if results is None:
                return_code = 1
        finally:
            print()
        if not shell:
            keep_results.append(results)

    if shell:
        return return_code
    return keep_results


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
    for workflow, graph, destination in zip(
        args.workflows, args.graphs, args.destinations
    ):
        convert_graph(graph, destination, **args.convert_options)
        print(f"Converted {workflow} -> {destination}")


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
