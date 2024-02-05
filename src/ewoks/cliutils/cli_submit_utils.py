from . import cli_execute_utils
from . import utils


def add_submit_parameters(parser):
    cli_execute_utils.add_execute_parameters(parser)
    parser.add_argument(
        "--wait",
        type=float,
        default=-1,
        help="Timeout for receiving the result (negative number to disable)",
    )
    parser.add_argument(
        "-c",
        "--cparameter",
        dest="cparameters",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="Celery parameters",
    )


def apply_submit_parameters(args):
    cli_execute_utils.apply_execute_parameters(args)
    args.cparameters = dict(utils.parse_option(item) for item in args.cparameters)
