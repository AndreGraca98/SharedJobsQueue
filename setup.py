from pathlib import Path
from subprocess import check_call

from setuptools import setup
from setuptools.command.install import install

script = f"""cp run_client.py JobsClient
cp run_server.py JobsServer
chmod +x JobsClient
chmod +x JobsServer
mkdir -p {Path.home()}/bin
cp -r jobs_queue {Path.home()}/bin
cp JobsClient {Path.home()}/bin
cp JobsServer {Path.home()}/bin
source ~/.profile"""


class PostInstallCommand(install):
    """Pre-installation for installation mode."""

    def run(self):
        install.run(self)
        [check_call(cmd.split()) for cmd in script.split("\n")]


setup(
    name="jobs-queue",
    version=open("jobs_queue/version.txt").read(),
    description="Add, remove, update and pause jobs in a queue that can be shared by multiple users to run scripts with different priority levels.",
    author="André Graça",
    author_email="andre.p.g@sapo.pt",
    platforms="Python",
    packages=["jobs_queue"],
    install_requires=[
        "easydict",
        "gpustat",
        "filelock",
        "pandas",
    ],
    cmdclass={
        "install": PostInstallCommand,
    },
)
