import os
from typing import List, Union

from .jobs import Job, Priority, State


def get_priority(priority: str):
    if not priority.isnumeric():
        return Priority[priority.upper()]

    assert int(priority) in list(
        range(1, len(Priority) + 1, 1)
    ), f"Priority not available. Expected: {Priority.__members__}. Got: {priority}"

    return Priority(int(priority))


class JobsQueue:
    jobs: List[Job]

    def __init__(self) -> None:
        self.jobs = list()

    def add(self, args) -> None:
        job = Job(
            id=self.get_new_valid_id(),
            priority=get_priority(args.priority),
            command=" ".join(args.command),
            needed_gpu_mem=args.gpu_mem,
            verbose_lvl=args.verbose,
        )

        print(f"Adding {job}")

        self.jobs.append(job)

    def update(self, args) -> None:
        if not args.id in self.get_jobs_ids():
            print(
                f"Job with id={args.id} does not exist. Choose from: {self.get_jobs_ids()}"
            )
            return

        job = self.get_job(args.id)

        if args.attr == "priority":
            new_value = get_priority(args.new_value)
        elif args.attr == "command":
            new_value = args.new_value
        else:
            print(f"Job has no attribute/can't update attribute={args.attr}")
            return

        msg = (
            f"Cant update {job} because user is not the same. Job belongs to {job.user}"
        )
        if not JobsQueue.is_action_allowed(job, msg):
            return

        print(
            f"Updating {job._str_lvl_(args.verbose)} . {args.attr}={getattr(job,args.attr)} -> {args.attr}={new_value}"
        )

        setattr(job, args.attr, new_value)

    def remove(self, args) -> None:
        # Removes a job by its id
        for _id in args.id:
            if not _id in self.get_jobs_ids():
                print(
                    f"Job with id={_id} does not exist in {self._str_lvl_(args.verbose)}"
                )
                continue

            job = self.get_job(_id)

            msg = f"Cant remove {job} because user is not the same. Job belongs to {job.user}"
            if not JobsQueue.is_action_allowed(job, msg):
                continue

            print(f"Removing {job._str_lvl_(args.verbose)}")

            self.jobs.pop(self.get_job_idx(job.id))

    def clear(self, args):
        if not args.yes:
            print(
                "Aborting clear command ! If you are sure you want to clear all jobs run the same command with the flag -y or --yes"
            )
            return

        print("Clearing all jobs...")
        self.jobs = list()

    def clear_finished(self, args):
        before = len(self.jobs)
        self.jobs = list(filter(lambda j: j.state is not State.FINISHED, self.jobs))
        print(f"Cleared {before - len(self.jobs)} finished jobs...")

    def show(self, args):
        if "id" in args and args.id is not None:
            job = self.get_job(args.id)
            if job is not None:
                print(job._str_lvl_(args.verbose))
                return

            print(f"Job with id={args.id} not found! Choose from {self.get_jobs_ids()}")

        elif "state" in args and args.state is not None:
            print(self._str_lvl_(args.verbose, state=args.state))
        else:
            print(self._str_lvl_(args.verbose))

    # ================================================================= #
    def is_action_allowed(job: Job, msg: str = None) -> bool:
        is_allowed = os.getlogin() == job.user
        if msg is not None and not is_allowed:
            print(msg)
        return is_allowed

    # ================================================================= #
    def get_next_job(self) -> Union[Job, None]:
        # Get urgent jobs first
        self.jobs = sorted(self.jobs, reverse=True)
        if len(self.jobs) == 0:
            # No jobs
            return

        jobs = list(filter(lambda j: j.state is State.WAITING, self.jobs))
        if len(jobs) == 0:
            # No pending jobs
            return

        job = jobs[0]
        job.update_state()
        return job

    def get_jobs_ids(self) -> List[int]:
        return [job.id for job in self.jobs]

    def get_new_valid_id(self) -> int:
        """Get a new id that does not exist yet"""
        valid_id = 0
        while valid_id in self.get_jobs_ids():
            valid_id += 1
        return valid_id

    def get_job_idx(self, id: int) -> Union[int, None]:
        if id not in self.get_jobs_ids():
            return

        return [job.id == id for job in self.jobs].index(True)

    def get_job(self, id: int) -> Union[Job, None]:
        idx = self.get_job_idx(id)

        if idx is None:
            return

        return self.jobs[idx]

    def __str__(self) -> str:
        return self._str_lvl_(-1)

    __repr__ = __str__

    def _str_lvl_(self, lvl, state: str = None):
        jobs = self.jobs

        if state is not None:
            if isinstance(state, str):
                state = (
                    State(int(state))
                    if state.strip("-").isnumeric()
                    else State[state.upper()]
                )
            else:
                raise TypeError(
                    f"Expected state type to be str or int. Got: {type(state)}"
                )
            jobs = filter(lambda j: j.state is state, self.jobs)

        return "Jobs:\n  " + "\n  ".join(
            [str(job._str_lvl_(lvl)) for job in sorted(jobs, reverse=True)]
        )


# ENDFILE
