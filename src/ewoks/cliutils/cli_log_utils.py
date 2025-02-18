import logging
import sys

LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def add_log_parameters(parser, default="warning"):
    parser.add_argument(
        "-l",
        "--log",
        type=str.lower,
        choices=list(LEVELS),
        default=default,
        help="Log level",
    )


def apply_log_parameters(args):
    logger = logging.getLogger()
    level = LEVELS[args.log]
    logger.setLevel(level)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)-8s - %(message)s"
    )

    class StdOutFilter(logging.Filter):
        def filter(self, record):
            return record.levelno < logging.WARNING

    class StdErrFilter(logging.Filter):
        def filter(self, record):
            return record.levelno >= logging.WARNING

    if level < logging.WARNING:
        h = logging.StreamHandler(sys.stdout)
        h.addFilter(StdOutFilter())
        h.setLevel(level)
        if formatter is not None:
            h.setFormatter(formatter)
        logger.addHandler(h)

    h = logging.StreamHandler(sys.stderr)
    h.addFilter(StdErrFilter())
    h.setLevel(level)
    if formatter is not None:
        h.setFormatter(formatter)
    logger.addHandler(h)
