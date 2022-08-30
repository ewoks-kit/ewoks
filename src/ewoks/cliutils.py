from ewokscore.cliutils import add_execute_parameters as _add_execute_parameters
from ewokscore.cliutils import apply_execute_parameters
from ewokscore.cliutils import add_convert_parameters  # noqa F401
from ewokscore.cliutils import apply_convert_parameters  # noqa F401


def add_execute_parameters(parser, shell=False):
    _add_execute_parameters(parser, shell=shell)
    parser.add_argument(
        "--binding",
        type=str,
        choices=["none", "dask", "ppf", "orange"],
        default="none",
        help="Task binding to be used",
    )


def add_submit_parameters(parser, shell=False):
    add_execute_parameters(parser, shell=shell)
    parser.add_argument(
        "--wait",
        type=float,
        default=-1,
        help="Timeout for receiving the result (negative number to disable)",
    )


def apply_submit_parameters(args, shell=False):
    apply_execute_parameters(args, shell=shell)
