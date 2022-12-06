#!/usr/bin/env python





try:
    from args import get_args
    from jobs_table import JOBS_TABLE_FILENAME
except ModuleNotFoundError:
    from .args import get_args
    from .jobs_table import JOBS_TABLE_FILENAME

__all__ = ["main_client"]


def main_client():
    JOBS_TABLE_FILENAME.parent.mkdir(parents=True, exist_ok=True)
    JOBS_TABLE_FILENAME.chmod(0o777) # Read, Write, Execute permissions so other users can change the files

    args = get_args(client=True)
    # print(args, "\n")
    args.operation(args)


if __name__ == "__main__":
    main_client()


# ENDFILE
