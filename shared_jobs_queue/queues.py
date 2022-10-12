import argparse
import os
from typing import List

from .jobs import Job, Priority


class JobsQueue:
    jobs: List[Job]

    def __init__(self) -> None:
        self.jobs = list()

    def add(self, args: argparse.Namespace) -> None:
        # Adds new job
        _priority = args.priority
        if _priority.isnumeric():
            assert int(_priority) in list(range(1, len(Priority)+1, 1)), f'Priority not available. Expected: {Priority.__members__}. Got: {_priority}'
            priority = Priority(int(_priority))
        else:
            priority = Priority[_priority.upper()]
            
        new_job = Job(
            priority=priority,
            command=' '.join(args.command),
            _id=self.get_new_valid_id(),
        )

        print(f"Adding new job {new_job} ...")

        self.jobs.append(new_job)

    def get_ids(self):
        return [job._id for job in self.jobs]

    def get_new_valid_id(self):
        """Get a new id that does not exist yet"""
        valid_id = 0
        while valid_id in self.get_ids():
            valid_id += 1
        return valid_id

    def remove(self, args: argparse.Namespace) -> None:
        # Removes a job by its id
        if -1 in args.id:
            print(f"Removing all jobs ids={list(map(lambda x: x._id, self.jobs))}...")
            self.jobs = list()
            return
            
        for _id in args.id:
            if not _id in [job._id for job in self.jobs]:
                print(f"Job with id={_id} does not exist in {self} ...")
                continue

            idx = [job._id == _id for job in self.jobs].index(True)

            assert (
                os.getlogin() == self.jobs[idx].user or os.getlogin() == "root" or os.getlogin() == "aime"
            ), f"Cant remove job with id {idx} because user is not the same. Job belongs to {self.jobs[idx].user}"

            print(f"Removing job {self.jobs[idx]} ...")

            self.jobs.pop(idx)

    def get_next_job(self) -> Job:
        # Get urgent jobs first
        self.jobs = sorted(self.jobs, reverse=True)
        if len(self.jobs) == 0:
            return

        return self.jobs.pop(0)

    def show(self, *args, **kwargs):
        print(self)
        
    def update(self, args: argparse.Namespace):
        if not args.id in [job._id for job in self.jobs]:
            print(f"Job with id={args.id} does not exist in {self} ...")
            return
            
        idx = [job._id == args.id for job in self.jobs].index(True)
            
        if args.attr in ['command', 'priority']:
            if args.attr == 'priority':
                if args.new_value.isnumeric():
                    assert int(args.new_value) in list(range(1, len(Priority)+1, 1)), f'Priority not available. Expected: {Priority.__members__}. Got: {args.new_value}'
                    new_value = Priority(int(args.new_value))
                else:
                    new_value = Priority[args.new_value.upper()]
            else:
                new_value = args.new_value
            
            print(f'Updating job(id={idx}, ...) . {args.attr}={getattr(self.jobs[idx],args.attr)} -> {args.attr}={new_value}')
            setattr(self.jobs[idx], args.attr, new_value)
            
            
        else:
            print(f'Job has no attribute < {args.attr} >')
        

    def __str__(self) -> str:
        return "Jobs:\n  " + "\n  ".join(
            [str(job) for job in sorted(self.jobs, reverse=True)]
        )

    __repr__ = __str__


# ENDFILE
