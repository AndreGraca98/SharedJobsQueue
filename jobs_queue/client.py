#!/usr/bin/env python


try:
    from args import get_args
except ModuleNotFoundError:
    from .args import get_args

__all__ = ["main_client"]


def main_client():

    args = get_args(client=True)
    # print(args, "\n")
    args.operation(args)


if __name__ == "__main__":
    main_client()


# ENDFILE
