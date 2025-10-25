import os
from typing import List


def parse_destinations(args) -> List[str]:
    dest_dirname = os.path.dirname(args.destination)
    basename = os.path.basename(args.destination)
    dest_basename, dest_ext = os.path.splitext(basename)
    if not dest_ext:
        dest_ext = dest_basename
        dest_basename = ""
        if not dest_ext.startswith("."):
            dest_ext = f".{dest_ext}"

    if len(args.workflows) == 1 and dest_basename:
        return [os.path.join(dest_dirname, f"{dest_basename}{dest_ext}")]

    destinations = list()
    for workflow in args.workflows:
        basename, _ = os.path.splitext(os.path.basename(workflow))
        destination = os.path.join(dest_dirname, f"{basename}{dest_basename}{dest_ext}")
        destinations.append(destination)

    return destinations
