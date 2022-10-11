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
            env=args.env,
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
        if not int(args.id) in [int(job._id) for job in self.jobs]:
            print(f"Job does not exist in {self} ...")
            return

        idx = [job._id == args.id for job in self.jobs].index(True)

        assert (
            os.getlogin() == self.jobs[idx].user or os.getlogin() == "root"
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

    def __str__(self) -> str:
        return "Jobs:\n  " + "\n  ".join(
            [str(job) for job in sorted(self.jobs, reverse=True)]
        )

    __repr__ = __str__


# ENDFILE
