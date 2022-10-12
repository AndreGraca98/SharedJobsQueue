import argparse
from typing import List

from .queues import JobsQueue

class VerboseAction(argparse.Action):
        def __init__(self, *args, **kwargs):
            kwargs['nargs'] = kwargs.get('nargs', '?')
            kwargs['default'] = kwargs.get('default', 1) # Verbose default level = 1
            super(VerboseAction, self).__init__(*args, **kwargs)
            self.option_dict=dict()
            
        def __call__(self, parser, args, values, option_string=None):
            if values is None:
                vals= 1
            else:
                try:
                    vals = int(values)
                except ValueError:
                    vals = values.count('v')+1
                    
            self.option_dict[option_string]=vals
            setattr(args, self.dest, max(self.option_dict.values()))
        
        
def get_server_parser():
    parser = argparse.ArgumentParser(
        "Server Jobs Queue",
        description="Run jobs from the jobs queue",
    )
    parser.add_argument("time", type=int, nargs='?',default=1, help="Idle time (s)")
    return parser
    
def get_client_parser():
    parser = argparse.ArgumentParser(
        "Client Jobs Queue",
        description="Add/Remove jobs to/from the jobs queue. If no options provided show current jobs on queue.",
    )
    def parse_verbose(parser):
        parser.add_argument("-v", "-V", '--verbose',  action=VerboseAction, help="Verbose")
        
    parse_verbose(parser=parser)
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
    parser_add.add_argument("command", type=str, action='store', nargs='+', help="Command to run")
    parser_add.set_defaults(operation=JobsQueue.add)
    parse_verbose(parser_add)

    parser_remove = subparser.add_parser("remove", help="Remove a task from the queue")
    parser_remove.add_argument("id", type=int, action='store', nargs='+',help="Job ids to remove from the queue. If -1 remove all jobs")
    parser_remove.set_defaults(operation=JobsQueue.remove)
    parse_verbose(parser_remove)

    parser_update = subparser.add_parser("update", help="Updates a task from the queue")
    parser_update.add_argument("id", type=int, help="Job id to update from the queue")
    parser_update.add_argument("attr", type=str, help="Job attribute to change")
    parser_update.add_argument("new_value", type=str, help="Job attribute new value")
    parser_update.set_defaults(operation=JobsQueue.update)
    parse_verbose(parser_update)

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
