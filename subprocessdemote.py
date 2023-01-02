#!/usr/bin/env python

import os
import pwd
import subprocess

# > python subprocessdemote.py
# > sudo python subprocessdemote.py


def demote(user_uid, user_gid):
    def result():
        os.setgid(user_gid)
        os.setuid(user_uid)

    return result


def exec_cmd(username):
    # get user info from username
    pw_record = pwd.getpwnam(username)
    homedir = pw_record.pw_dir
    user_uid = pw_record.pw_uid
    user_gid = pw_record.pw_gid

    print("pw_record:", pw_record)

    env = os.environ.copy()
    env.update(
        {
            "HOME": homedir,
            "LOGNAME": username,
            "PWD": os.getcwd(),
            "FOO": "bar",
            "USER": username,
        }
    )

    print(os.environ)
    print(env)

    # execute the command
    proc = subprocess.Popen(
        ["echo $USER; touch /home/pedromartins/testtt"],
        shell=True,
        env=env,
        preexec_fn=demote(user_uid, user_gid),
    )
    proc.wait()


if __name__ == "__main__":

    exec_cmd("pedromartins")
    exec_cmd("andregraca")
