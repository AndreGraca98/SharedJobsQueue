from setuptools import setup

with open("jobs_queue/version.txt") as f:
    version = f.read()


setup(
    name="jobs-queue",
    version=version,
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
)
