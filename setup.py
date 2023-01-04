import json
from pathlib import Path
from subprocess import check_call

from setuptools import setup
from setuptools.command.install import install

script = f"""
cp run_client_cmds.py jobsclient
cp run_server_cmds.py jobsserver-cmds
cp run_server_queue.py jobsserver-queue
cp run_user_settings.py jobsusersettings

chmod +x jobsclient
chmod +x jobsserver-cmds
chmod +x jobsserver-queue
chmod +x jobsusersettings

mkdir -p {Path.home()}/bin

cp -r jobs_queue {Path.home()}/bin
cp jobsclient {Path.home()}/bin
cp jobsserver-cmds {Path.home()}/bin
cp jobsserver-queue {Path.home()}/bin
cp jobsusersettings {Path.home()}/bin

"""


class PostInstallCommand(install):
    """Pre-installation for installation mode."""

    def run(self):
        install.run(self)
        [check_call(cmd.split()) for cmd in script.split("\n") if cmd]


setup(
    name="jobs-queue",
    version=json.load(open("jobs_queue/version.json"))["version"],
    description="Add, remove, update and pause jobs in a queue that can be shared by multiple users to run scripts with different priority levels.",
    author="André Graça",
    author_email="andre.p.g@sapo.pt",
    platforms="Python",
    packages=["jobs_queue"],
    install_requires=[
        "easydict",
        "filelock",
        "pandas",
        "psutil"
    ],
    cmdclass={
        "install": PostInstallCommand,
    },
)
