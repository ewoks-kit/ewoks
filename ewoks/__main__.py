import sys
import argparse

from pprint import pformat
from ewokscore import cliutils
from .bindings import execute_graph
from .bindings import convert_graph


def create_argument_parser(shell=False):
    parser = argparse.ArgumentParser(
        description="Esrf WOrKflow Sytem CLI", prog="ewoks"
    )

    subparsers = parser.add_subparsers(help="Commands", dest="command")
    execute = subparsers.add_parser("execute", help="Execute a workflow")
    convert = subparsers.add_parser("convert", help="Convert a workflow")

    execute.add_argument(
        "--binding",
        type=str,
        choices=["none", "dask", "ppf", "orange"],
        default="none",
        help="Task binding to be used",
    )
    cliutils.add_execute_parameters(execute, shell=shell)
    cliutils.add_convert_parameters(convert, shell=shell)

    return parser


def command_execute(args, shell=False):
    cliutils.apply_execute_parameters(args, shell=shell)
    results = execute_graph(args.graph, binding=args.binding, **args.execute_options)
    print("Result of workflow '%s':\n%s" % (args.workflow, pformat(results)))

    if shell:
        if results is None:
            return 1
        else:
            return 0
    else:
        return results


def command_convert(args, shell=False):
    cliutils.apply_convert_parameters(args, shell=shell)
    convert_graph(args.graph, args.destination, **args.convert_options)


def command_default(args, shell=False):
    if shell:
        return 0
    else:
        return None


def main(argv=None, shell=True):
    parser = create_argument_parser(shell=shell)

    if argv is None:
        argv = sys.argv
    args, _ = parser.parse_known_args(argv[1:])

    if args.command == "execute":
        return command_execute(args, shell=shell)
    elif args.command == "convert":
        return command_convert(args, shell=shell)
    else:
        return command_default(args, shell=shell)


if __name__ == "__main__":
    sys.exit(main())
