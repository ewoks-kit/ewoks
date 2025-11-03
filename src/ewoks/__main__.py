import sys
import traceback
from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
from argparse import Namespace
from pprint import pprint
from subprocess import CalledProcessError
from typing import Any
from typing import List
from typing import Literal
from typing import Optional
from typing import Union

from ewoksutils.cli_utils import cli_cancel_utils
from ewoksutils.cli_utils import cli_execute_utils
from ewoksutils.cli_utils import cli_submit_utils
from ewoksutils.cli_utils.cli_argparse import add_to_parser

from .bindings import _load_graph
from .bindings import convert_graph
from .bindings import execute_graph
from .bindings import install_graph
from .bindings import show_graph
from .cli_utils import cli_convert_utils
from .cli_utils import cli_install_utils
from .cli_utils import cli_show_utils
from .errors import AbortException

try:
    from ewoksjob.cli_utils.cancel import command_cancel as _command_cancel
    from ewoksjob.cli_utils.submit import command_submit as _command_submit
except ImportError:
    _command_submit = None
    _command_cancel = None


def create_argument_parser(shell: bool = False) -> ArgumentParser:
    parser = ArgumentParser(
        description="Extensible WOrKflow System CLI",
        prog="ewoks",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(help="Commands", dest="command")
    execute = subparsers.add_parser(
        "execute",
        help="Execute a workflow",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    submit = subparsers.add_parser(
        "submit",
        help="Schedule a workflow execution",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    cancel = subparsers.add_parser(
        "cancel",
        help="Abort a scheduled workflow execution",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    convert = subparsers.add_parser(
        "convert",
        help="Convert a workflow",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    install = subparsers.add_parser(
        "install",
        help="Install requirements of a workflow",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    show = subparsers.add_parser(
        "show",
        help="Show workflow information",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    add_to_parser(execute, cli_execute_utils.execute_arguments(shell=shell))
    add_to_parser(submit, cli_submit_utils.submit_arguments(shell=shell))
    add_to_parser(cancel, cli_cancel_utils.cancel_arguments(shell=shell))
    add_to_parser(convert, cli_convert_utils.convert_arguments(shell=shell))
    add_to_parser(install, cli_install_utils.install_arguments(shell=shell))
    add_to_parser(show, cli_show_utils.show_arguments(shell=shell))
    return parser


def command_execute(
    cli_args: Namespace, shell: bool = False
) -> Union[List[dict], Literal[0, 1]]:
    cli_execute_utils.parse_execute_argument(cli_args, shell=shell)

    return_code = 0
    keep_results = []
    for workflow, graph in zip(cli_args.workflows, cli_args.graphs):
        print("###################################")
        print(f"# Execute workflow '{workflow}'")
        print("###################################")
        try:
            results = execute_graph(
                graph, engine=cli_args.engine, **cli_args.execute_options
            )
        except Exception as ex:
            traceback.print_exc()
            print("FAILED")
            results = ex
            return_code = 1
        else:
            if cli_args.outputs == "none":
                if results is None:
                    print("FAILED")
                else:
                    print("FINISHED")
            else:
                print("")
                print("RESULTS:")
                pprint(results)
                print("")
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


def command_submit(
    cli_args: Namespace, shell: bool = False
) -> Union[List[dict], Literal[0, 1]]:
    if _command_submit is None:
        raise RuntimeError("requires the 'ewoksjob>=1.3' package")
    return _command_submit(cli_args, _convert_graph=_load_graph, shell=shell)


def command_cancel(cli_args: Namespace, shell: bool = False) -> Optional[Literal[0, 1]]:
    if _command_cancel is None:
        raise RuntimeError("requires the 'ewoksjob>=1.3' package")
    return _command_cancel(cli_args, shell)


def command_convert(
    cli_args: Namespace, shell: bool = False
) -> Optional[Literal[0, 1]]:
    cli_convert_utils.parse_convert_arguments(cli_args, shell=shell)
    for workflow, graph, destination in zip(
        cli_args.workflows, cli_args.graphs, cli_args.destinations
    ):
        convert_graph(graph, destination, **cli_args.convert_options)
        print(f"Converted {workflow} -> {destination}")
    if shell:
        return 0
    return None


def command_install(
    cli_args: Namespace, shell: bool = False
) -> Optional[Literal[0, 1]]:
    cli_install_utils.parse_install_arguments(cli_args, shell=shell)
    for workflow, graph in zip(cli_args.workflows, cli_args.graphs):
        try:
            install_graph(graph, cli_args.yes, cli_args.python)
        except CalledProcessError as e:
            print(f"Install failed for {workflow}: {e}")
        except AbortException:
            print(f"Install aborted for {workflow}")
        else:
            print(f"Installed requirements for {workflow}")
    if shell:
        return 0
    return None


def command_show(cli_args: Namespace, shell: bool = False) -> Optional[Literal[0, 1]]:
    cli_show_utils.parse_show_arguments(cli_args, shell=shell)
    for workflow, graph in zip(cli_args.workflows, cli_args.graphs):
        show_graph(graph, original_source=workflow, **cli_args.show_options)
    if shell:
        return 0
    return None


def command_default(
    cli_args: Namespace, shell: bool = False
) -> Optional[Literal[0, 1]]:
    if shell:
        return 1
    return None


def main(argv=None, shell: bool = True) -> Union[Any, Literal[0, 1]]:
    parser = create_argument_parser(shell=shell)

    if argv is None:
        argv = sys.argv
    cli_args = parser.parse_args(argv[1:])

    if cli_args.command == "execute":
        return command_execute(cli_args, shell=shell)
    elif cli_args.command == "submit":
        return command_submit(cli_args, shell=shell)
    elif cli_args.command == "cancel":
        return command_cancel(cli_args, shell=shell)
    elif cli_args.command == "convert":
        return command_convert(cli_args, shell=shell)
    elif cli_args.command == "install":
        return command_install(cli_args, shell=shell)
    elif cli_args.command == "show":
        return command_show(cli_args, shell=shell)
    else:
        parser.print_help()
        return command_default(cli_args, shell=shell)


if __name__ == "__main__":
    sys.exit(main())
