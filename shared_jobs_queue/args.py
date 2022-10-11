import argparse
from typing import List

from .queues import JobsQueue


def get_server_parser():
    parser = argparse.ArgumentParser(
        "Server Jobs Queue",
        description="Run jobs from the jobs queue",
    )
    parser.add_argument("time", type=str, nargs='?',default=1, help="Idle time (s)")
    return parser
    
def get_client_parser():
    parser = argparse.ArgumentParser(
        "Client Jobs Queue",
        description="Add/Remove jobs to/from the jobs queue. If no options provided show current jobs on queue.",
    )
    parser.set_defaults(operation=JobsQueue.show)
    subparser = parser.add_subparsers()
    parser_add = subparser.add_parser("add", help="Add a task to the queue")

    parser_add.add_argument(
        "-p",
        "-P",
        "--priority",
        default="normal",
        type=str,
        dest='priority',
        help="Command priority. low (1), medium/normal (2), high (3) or urgent (4)",
    )
    parser_add.add_argument("env", type=str, help="Environment to run the command")  
    parser_add.add_argument("command", type=str, action='store', nargs='+', help="Command to run")

    parser_add.set_defaults(operation=JobsQueue.add)

    parser_remove = subparser.add_parser("remove", help="Remove a task from the queue")
    parser_remove.add_argument("id", type=int, help="Job id to remove from the queue")
    parser_remove.set_defaults(operation=JobsQueue.remove)

    return parser


def get_args(client_args:bool=True):
    if client_args:
        return get_client_parser().parse_args()
    return get_server_parser().parse_args()


def get_args_from_str(_str: str, client_args:bool=True):
    if client_args:
        return get_client_parser().parse_args(_str.split())
    return get_server_parser().parse_args(_str.split())


def get_args_from_list(_list: List, client_args:bool=True):
    if client_args:
        return get_client_parser().parse_args(_list)
    return get_server_parser().parse_args(_list)


# ENDFILE
