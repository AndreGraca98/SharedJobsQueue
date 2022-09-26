import argparse
from typing import List

from .queues import JobsQueue


def get_parser():
    parser = argparse.ArgumentParser(
        "Jobs Queue",
        description="Add/Remove jobs to/from the jobs queue. If no options provided show current jobs on queue.",
    )
    parser.set_defaults(operation=JobsQueue.show)
    subparser = parser.add_subparsers()
    parser_add = subparser.add_parser("add", help="Add a task to the queue")

    parser_add.add_argument(
        "-p",
        "--priority",
        default="normal",
        type=str,
        help="Command priority. low, medium/normal, high or urgent",
    )
    parser_add.add_argument("command", type=str, help="Command to run")  # arg
    # parser_add.add_argument("-c","--command", type=str, help="Command") # kwarg

    parser_add.set_defaults(operation=JobsQueue.add)

    parser_remove = subparser.add_parser("remove", help="Remove a task from the queue")
    parser_remove.add_argument("id", type=int, help="Job id to remove from the queue")
    parser_remove.set_defaults(operation=JobsQueue.remove)

    return parser


def get_args():
    return get_parser().parse_args()


def get_args_from_str(_str: str):
    return get_parser().parse_args(_str.split())


def get_args_from_list(_list: List):
    return get_parser().parse_args(_list)


# ENDFILE
