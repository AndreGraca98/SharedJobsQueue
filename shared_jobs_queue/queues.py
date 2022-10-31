import argparse
import os
from typing import List, Union

from .jobs import Job, Priority


class JobsQueue:
    jobs: List[Job]

    def __init__(self) -> None:
        self.jobs = list()

    def add(self, args: argparse.Namespace) -> None:
        # Adds new job
        _priority = args.priority
        if _priority.isnumeric():
            assert int(_priority) in list(
                range(1, len(Priority) + 1, 1)
            ), f"Priority not available. Expected: {Priority.__members__}. Got: {_priority}"
            priority = Priority(int(_priority))
        else:
            priority = Priority[_priority.upper()]

        new_job = Job(
            priority=priority,
            command=" ".join(args.command),
            _id=self.get_new_valid_id(),
            verbose_lvl=args.verbose,
        )

        if args.verbose > 0:
            print(f"Adding new job {new_job}")

        self.jobs.append(new_job)

    def get_ids(self):
        return [job._id for job in self.jobs]
    
    def get_job_with_id(self, _id:int)->Union[Job, None]:
        if _id not in self.get_ids():
            return
        
        return self.jobs[[job._id == _id for job in self.jobs].index(True)]

    def get_new_valid_id(self):
        """Get a new id that does not exist yet"""
        valid_id = 0
        while valid_id in self.get_ids():
            valid_id += 1
        return valid_id

    def remove(self, args: argparse.Namespace) -> None:
        # Removes a job by its id
        if -1 in args.id:
            if args.verbose > 0:
                print(
                    f"Removing all jobs with ids={list(map(lambda x: x._id, self.jobs))}..."
                )
            self.jobs = list()
            return

        for _id in args.id:
            if not _id in [job._id for job in self.jobs]:
                if args.verbose > 0:
                    print(
                        f"Job with id={_id} does not exist in {self._str_lvl(args.verbose)} ..."
                    )
                continue

            idx = [job._id == _id for job in self.jobs].index(True)

            assert (
                os.getlogin() == self.jobs[idx].user
                or os.getlogin() == "root"
                or os.getlogin() == "aime"
            ), f"Cant remove job with id {idx} because user is not the same. Job belongs to {self.jobs[idx].user}"

            if args.verbose > 0:
                print(f"Removing job {self.jobs[idx]._str_lvl_(args.verbose)} ...")

            self.jobs.pop(idx)

    def get_next_job(self) -> Union[Job, None]:
        # Get urgent jobs first
        self.jobs = sorted(self.jobs, reverse=True)
        if len(self.jobs) == 0:
            return

        return self.jobs.pop(0)

    def show(self, args, **kwargs):
        if 'id' in args and args.id is not None:
            print(self.show_id(args))
        else:
            print(self._str_lvl(args.verbose))

    def show_id(self, args):
        job = self.get_job_with_id(args.id)
        if not job:
            return f'Job with id={args.id} not found! Choose from {self.get_ids()}'
        job.verbose_lvl = args.verbose
        return job
        

    def update(self, args: argparse.Namespace):
        if not args.id in [job._id for job in self.jobs]:
            if args.verbose > 0:
                print(
                    f"Job with id={args.id} does not exist in {self._str_lvl(args.verbose)} ..."
                )
            return

        idx = [job._id == args.id for job in self.jobs].index(True)

        if args.attr in ["command", "priority"]:
            if args.attr == "priority":
                if args.new_value.isnumeric():
                    assert int(args.new_value) in list(
                        range(1, len(Priority) + 1, 1)
                    ), f"Priority not available. Expected: {Priority.__members__}. Got: {args.new_value}"
                    new_value = Priority(int(args.new_value))
                else:
                    new_value = Priority[args.new_value.upper()]
            else:
                new_value = args.new_value

            job = self.jobs[idx]

            print(
                f"Updating {job._str_lvl_(args.verbose)} . {args.attr}={getattr(job,args.attr)} -> {args.attr}={new_value}"
            )
            setattr(job, args.attr, new_value)

        else:
            if args.verbose > 0:
                print(f"Job has no attribute < {args.attr} >")

    def __str__(self) -> str:
        return "Jobs:\n  " + "\n  ".join(
            [str(job) for job in sorted(self.jobs, reverse=True)]
        )

    def _str_lvl(self, lvl):
        for job in self.jobs:
            job.verbose_lvl = lvl

        return self

    __repr__ = __str__


# ENDFILE
