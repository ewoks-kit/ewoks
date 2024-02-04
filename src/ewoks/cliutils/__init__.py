from . import clilogutils
from . import cliexecuteutils
from . import cliconvertutils
from . import clisubmitutils


def add_execute_parameters(parser, shell=False):
    if shell:
        clilogutils.add_log_parameters(parser)
    cliexecuteutils.add_execute_parameters(parser)


def apply_execute_parameters(args, shell=False):
    if shell:
        clilogutils.apply_log_parameters(args)
    cliexecuteutils.apply_execute_parameters(args)


def add_convert_parameters(parser, shell=False):
    if shell:
        clilogutils.add_log_parameters(parser)
    cliconvertutils.add_convert_parameters(parser)


def apply_convert_parameters(args, shell=False):
    if shell:
        clilogutils.apply_log_parameters(args)
    cliconvertutils.apply_convert_parameters(args)


def add_submit_parameters(parser, shell=False):
    if shell:
        clilogutils.add_log_parameters(parser)
    clisubmitutils.add_submit_parameters(parser)


def apply_submit_parameters(args, shell=False):
    if shell:
        clilogutils.apply_log_parameters(args)
    clisubmitutils.apply_submit_parameters(args)
