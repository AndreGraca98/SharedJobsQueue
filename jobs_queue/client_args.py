import argparse
from typing import List

from .common import operations

__all__ = [
    "get_client_parser",
    "get_args",
    "get_args_from_str",
    "get_args_from_list",
    "operations",
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


def get_client_parser():
    parser = argparse.ArgumentParser(
        "Client Jobs Queue",
        description="Add/Update/Remove jobs to/from the jobs queue. If no options provided show current jobs on queue.",
    )

    def parse_verbose(parser):
        parser.add_argument(
            "-v", "-V", "--verbose", action=VerboseAction, help="Verbose"
        )

    parse_verbose(parser=parser)
    parser.set_defaults(operation=operations.show)
    subparser = parser.add_subparsers()

    # Show
    def add_subparser_queue_show(subparser):
        parser_show_id = subparser.add_parser("show", help="Show a task in the queue")
        parser_show_id.add_argument(
            "id", nargs="?", type=int, default=None, help="Show job with specified id"
        )
        parser_show_id.set_defaults(operation=operations.show)
        parse_verbose(parser=parser_show_id)

    # Show state
    def add_subparser_queue_show_state(subparser):
        parser_show_state = subparser.add_parser(
            "show-state", help="Show tasks with state in the queue"
        )
        parser_show_state.add_argument(
            "state",
            nargs="?",
            type=str,
            default=None,
            help="Show jobs with specified state",
        )
        parser_show_state.set_defaults(operation=operations.show)
        parse_verbose(parser=parser_show_state)

    # Add
    def add_subparser_queue_add(subparser):
        parser_add = subparser.add_parser("add", help="Add a task to the queue")
        parser_add.add_argument(
            "command", type=str, action="store", nargs="+", help="Command to run"
        )
        parser_add.add_argument(
            "--env",
            "--envname",
            type=str,
            default="base",
            dest="envname",
            help="Conda environment name",
        )
        parser_add.add_argument(
            "--wd",
            "--working_dir",
            type=str,
            default=None,
            dest="working_dir",
            help="Working directory. If not set uses the dir associated with the env name",
        )
        parser_add.add_argument(
            "-p",
            "-P",
            "--priority",
            default="normal",
            type=str,
            dest="priority",
            help="Command priority. low (1), medium/normal (2), high (3) or urgent (4)",
        )
        parser_add.add_argument(
            "--mem",
            "--gpu_mem",
            "--needed",
            "--needed_mem",
            "--needed_gpu_mem",
            dest="gpu_mem",
            type=float,
            default=0,
            help="GPU memory in MB. If cmd does not require the usage of graphical memory set --gpu_mem to 0.",
        )
        parser_add.set_defaults(operation=operations.add)
        parse_verbose(parser=parser_add)

    # Remove
    def add_subparser_queue_remove(subparser):
        parser_remove = subparser.add_parser(
            "remove", help="Remove a task from the queue"
        )
        parser_remove.add_argument(
            "ids",
            type=int,
            action="store",
            nargs="+",
            help="Job ids to remove from the queue",
        )
        parser_remove.set_defaults(operation=operations.remove)
        parse_verbose(parser=parser_remove)

    # Update
    def add_subparser_queue_update(subparser):
        parser_update = subparser.add_parser(
            "update", help="Updates a task from the queue"
        )
        parser_update.add_argument(
            "id", type=int, help="Job id to update from the queue"
        )
        parser_update.add_argument(
            "attr",
            type=str,
            choices={"priority", "command", "gpu_mem"},
            help="Job attribute to change",
        )
        parser_update.add_argument(
            "new_value", type=str, help="Job attribute new value"
        )
        parser_update.set_defaults(operation=operations.update)
        parse_verbose(parser=parser_update)

    # Pause/UnPause
    def add_subparser_queue_pause_resume(parser):
        op = parser.prog.split()[~0]

        subparser_pause = parser.add_subparsers(
            dest="op",
            required=True,
            description=f"{op.capitalize()} jobs with ids, priority or all waiting jobs",
        )

        parser_pause_id = subparser_pause.add_parser(
            "ids", description=f"{op.capitalize()} tasks with ids in the queue"
        )

        parser_pause_id.add_argument(
            "ids",
            type=int,
            action="store",
            nargs="+",
            help="Job ids ",
        )
        parser_pause_id = subparser_pause.add_parser(
            "priority",
            description=f"{op.capitalize()} tasks with priority in the queue",
        )

        parser_pause_id.add_argument(
            "priority",
            type=str,
            help="Jobs priority ",
        )

        subparser_pause.add_parser(
            "all", description=f"{op.capitalize()} all waiting tasks in the queue"
        )

    # Pause
    def add_subparser_queue_pause(subparser):
        parser_pause = subparser.add_parser("pause", help="Pause tasks from the queue")
        add_subparser_queue_pause_resume(parser_pause)

        parser_pause.set_defaults(operation=operations.pause)
        parse_verbose(parser=parser_pause)

    # Unpause
    def add_subparser_queue_resume(subparser):
        parser_resume = subparser.add_parser(
            "resume", help="Resume tasks from the queue"
        )
        add_subparser_queue_pause_resume(parser_resume)

        parser_resume.set_defaults(operation=operations.resume)
        parse_verbose(parser=parser_resume)

    # Clear
    def add_subparser_queue_clear(subparser):
        parser_clear = subparser.add_parser(
            "clear", help="Clears all tasks from the queue"
        )
        parser_clear.add_argument(
            "-y", "--yes", action="store_true", help="Clear Job Queue"
        )
        parser_clear.set_defaults(operation=operations.clear)

    # Clear State
    def add_subparser_queue_clear_state(subparser):
        parser_clear_state = subparser.add_parser(
            "clear-state", help="Clears all state tasks from the queue"
        )
        parser_clear_state.add_argument("state", type=str, help="Clear Job State")
        parser_clear_state.set_defaults(operation=operations.clear_state)

    # Info
    def add_subparser_queue_info(subparser):
        parser_info = subparser.add_parser("info", help="Shows queue info")
        parser_info.set_defaults(operation=operations.info)

    # Kill pid
    def add_subparser_queue_kill_pid(subparser):
        parser_kill_pid = subparser.add_parser(
            "kill", help="kills a running process by its id"
        )
        parser_kill_pid.add_argument("id", type=int, help="Kill Job")
        parser_kill_pid.add_argument(
            "-y", "--yes", action="store_true", help="If certain use flag -y/--yes"
        )
        parser_kill_pid.set_defaults(operation=operations.kill)

    # Retry job
    def add_subparser_queue_retry_job(subparser):
        parser_retry = subparser.add_parser(
            "retry", help="Retries runing a process by its id"
        )
        parser_retry.add_argument("id", type=int, help="Job id")

        parser_retry.set_defaults(operation=operations.retry)

    add_subparser_queue_show(subparser)
    add_subparser_queue_show_state(subparser)
    add_subparser_queue_add(subparser)
    add_subparser_queue_remove(subparser)
    add_subparser_queue_update(subparser)
    add_subparser_queue_pause(subparser)
    add_subparser_queue_resume(subparser)
    add_subparser_queue_clear(subparser)
    add_subparser_queue_clear_state(subparser)
    add_subparser_queue_info(subparser)
    add_subparser_queue_kill_pid(subparser)
    add_subparser_queue_retry_job(subparser)

    return parser


def get_args():
    return get_client_parser().parse_args()


def get_args_from_str(_str: str):
    return get_client_parser().parse_args(_str.split())


def get_args_from_list(_list: List):
    return get_client_parser().parse_args(_list)


# ENDFILE
