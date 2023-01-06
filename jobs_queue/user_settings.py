import argparse
import datetime
import json
import os
import pwd
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Union

from . import JOBS_TABLE_FILENAME

USER_SETTINGS = Dict[str, Dict[str, Path]]
SETTINGS = Dict[str, USER_SETTINGS]
# dict(USERNAME = dict(ENVNAME = dict(env_path=..., working_dir=...))))
all_users_settings: SETTINGS = dict()


def get_local_usernames() -> List[str]:
    return [p.pw_name for p in pwd.getpwall() if 1000 <= p.pw_uid <= 2000]


def get_home_path(username: str) -> Path:
    return Path("/home") / username


def get_conda_envs_path(username: str) -> Path:
    return get_home_path(username) / "anaconda3/envs/"


def get_available_conda_envs(username: str):
    return list(get_conda_envs_path(username).glob("[!.]*"))


def get_user_env_and_wdir_paths(
    username: str, envname: str, working_dir: Path
) -> Dict[str, Path]:
    """
    Returns:
        Dict[str, Path]: env_path, working_dir
    """
    return dict(
        env_path=str(get_conda_envs_path(username) / envname / "bin/python"),
        working_dir=str(working_dir),
    )


def create_new_user_settings(username: str) -> USER_SETTINGS:
    """Creates user settings

    Args:
        username (str): Username

    Returns:
        Dict[str, Dict[str, Path]]: dictionary with environment names as keys
        and env_path, working_dir as values
    """
    local_users = get_local_usernames()
    if username not in local_users:
        raise ValueError(f"User '{username}' does not exist. Choose from {local_users}")

    uhome = get_home_path(username)  # User home path
    usettings = dict()
    # usettings["base"] = get_user_env_and_wdir_paths(username, "base", uhome)
    for env in get_available_conda_envs(username):
        usettings[env.stem] = get_user_env_and_wdir_paths(username, env, uhome)

    return usettings


def update_settings(
    ausettings: SETTINGS,
    username: str,
    new_envname: str = None,
    working_dir: Path = None,
) -> SETTINGS:
    if username not in ausettings:
        ausettings[username] = create_new_user_settings(username)

    if new_envname is None:
        return ausettings

    if new_envname not in ausettings[username]:
        print(f"Invalid environment for '{username}': {new_envname}")
        return ausettings

    if working_dir is None:
        print(
            f"working_dir is 'None'. Using home dir as working directory for '{new_envname}'"
        )
        working_dir = Path.home()

    ausettings[username].update(
        {
            new_envname: get_user_env_and_wdir_paths(
                username, new_envname, Path(working_dir).resolve()
            )
        }
    )

    return ausettings


def create_settings(*args, **kwargs):
    settings = all_users_settings
    for username in get_local_usernames():
        settings = update_settings(
            ausettings=settings,
            username=username,
        )
    save_settings(settings)


def save_settings(ausettings: SETTINGS) -> None:
    """Saves settings

    Args:
        ausettings (SETTINGS): all users settings
    """
    os.umask(0000)  # Everyone can read/write
    settings_file = JOBS_TABLE_FILENAME.parent / "USER_SETTINGS.json"
    settings_file.touch(mode=0o777, exist_ok=True)

    with open(settings_file, "w") as f:
        json.dump(ausettings, f, indent=2, sort_keys=False)


def read_settings() -> SETTINGS:
    """Reads settings. If file doesnt exist create new

    Returns:
        SETTINGS: all users settings
    """
    settings_file = JOBS_TABLE_FILENAME.parent / "USER_SETTINGS.json"

    try:
        with open(settings_file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File does not exist: {settings_file.resolve()}. Creating new...")
        create_settings()
        return read_settings()


def get_user_paths(username: str, envname: str) -> Dict[str, str]:
    """Get env path and associated working dir for a user"""
    all_paths = read_settings()

    if not Path(envname).exists():
        return all_paths[username][envname]

    for k, v in all_paths[username].items():
        if v["env_path"] == envname:
            return v

    raise ValueError


def info(args):
    settings_file = JOBS_TABLE_FILENAME.parent / "USER_SETTINGS.json"

    pholder = " --- "
    if settings_file.exists():
        mtime = datetime.datetime.fromtimestamp(settings_file.stat().st_mtime)
        mode = settings_file.stat().st_mode
        size = settings_file.stat().st_size
    else:
        mtime = pholder
        mode = pholder
        size = pholder

    msg = f"""User Settings:
  dir: {settings_file.parent}
  filename: {settings_file}
  exists: {settings_file.exists()}
  mode: {mode}
  modified: {mtime}
  size: {size} B
"""

    print(msg)


def get_parser():
    parser = argparse.ArgumentParser()
    parser.set_defaults(operation=info)

    subparsers = parser.add_subparsers()

    parser_add = subparsers.add_parser("show")
    parser_add.set_defaults(operation=lambda args: pprint(read_settings()))

    parser_update = subparsers.add_parser("update")
    parser_update.add_argument("user", type=str, help="Add user settings")
    parser_update.add_argument(
        "-e",
        "--env",
        "--envname",
        type=str,
        required=True,
        dest="envname",
        help="User conda environment name",
    )
    parser_update.add_argument(
        "--wd",
        "--working_dir",
        type=str,
        required=True,
        dest="working_dir",
        help="Env associated working directory",
    )

    def update_user_settings(args):
        settings = read_settings()
        settings = update_settings(
            ausettings=settings,
            username=args.user,
            new_envname=args.envname,
            working_dir=args.working_dir,
        )
        save_settings(settings)
        print("Updated...")
        pprint(read_settings())

    parser_update.set_defaults(operation=update_user_settings)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    args.operation(args)


if __name__ == "__main__":
    main()
