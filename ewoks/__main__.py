import sys
import importlib


def import_binding(binding: str):
    if binding == "none":
        binding = "ewokscore"
    else:
        binding = "ewoks" + binding
    return importlib.import_module(binding)


def main(argv=None):
    import argparse

    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description="Esrf WOrKflow Sytem CLI", prog="ewoks"
    )

    subparsers = parser.add_subparsers(help="Commands")
    execute = subparsers.add_parser("execute", help="Execute a graph")

    execute.add_argument(
        "graph",
        type=str,
        help="URI to a graph (e.g. JSON filename)",
    )
    execute.add_argument(
        "--scheduler",
        type=str,
        choices=["none", "dask", "ppf", "orange"],
        default="none",
        help="Task scheduler to be used",
    )
    execute.add_argument(
        "--root_uri",
        type=str,
        default="",
        help="Root for saving task results",
    )
    execute.add_argument(
        "--scheme",
        type=str,
        choices=["nexus", "json"],
        default="nexus",
        help="Default task result format",
    )

    args, _ = parser.parse_known_args(argv[1:])

    varinfo = {"root_uri": args.root_uri, "scheme": args.scheme}

    binding = import_binding(args.scheduler)
    execute_graph = getattr(binding, "execute_graph")
    execute_graph(args.graph, varinfo=varinfo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
