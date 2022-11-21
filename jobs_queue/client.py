from args import get_args
from jobs_table import JOBS_TABLE_FILENAME


def run():
    JOBS_TABLE_FILENAME.parent.mkdir(parents=True, exist_ok=True)

    args = get_args(client=True)
    # print(args, "\n")
    args.operation(args)


if __name__ == "__main__":
    run()


# ENDFILE
