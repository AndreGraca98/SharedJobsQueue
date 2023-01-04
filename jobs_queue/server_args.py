import argparse
from typing import List

__all__ = [
    "get_server_parser",
    "get_args",
    "get_args_from_str",
    "get_args_from_list",
]


class VerboseAction(argparse.Action):
    def __init__(self, *args, **kwargs):
        kwargs["nargs"] = kwargs.get("nargs", "?")
        kwargs["default"] = kwargs.get("default", 1)  # Verbose default level = 1
        super(VerboseAction, self).__init__(*args, **kwargs)
        self.option_dict = dict()

    def __call__(self, parser, args, values, option_string=None):
        if values is None:
            vals = 1
        else:
            try:
                vals = int(values)
            except ValueError:
                vals = values.count("v") + 1

        self.option_dict[option_string] = vals
        setattr(args, self.dest, max(self.option_dict.values()))


def get_server_parser():
    parser = argparse.ArgumentParser(
        "Server Jobs Queue",
        description="Run jobs from the jobs queue",
    )
    parser.add_argument(
        "time",
        type=int,
        nargs="?",
        default=60,
        help="Idle time (s). NOTE: It is recommended to use at least 60 seconds of interval time when using this tool to train diferent experiments using gpus so they have enough time to load the model and data instead of throwing an error.",
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=1,
        help="Number of jobs allowed to run at the same time",
    )
    return parser


def get_args():
    return get_server_parser().parse_args()


def get_args_from_str(_str: str):
    return get_server_parser().parse_args(_str.split())


def get_args_from_list(_list: List):
    return get_server_parser().parse_args(_list)


# ENDFILE
