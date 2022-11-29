from setuptools import setup

import jobs_queue

setup(
    name="jobsqueue",
    version=jobs_queue.__version__,
    description="A package to run jobs that may or may not require graphical memory",
    author="André Graça",
    author_email="andre.p.g@sapo.pt",
    platforms="Python",
    packages=["jobs_queue", "run_client", "run_server"],
    install_requires=[
        "easydict",
        "gpustat",
        "filelock",
        "pandas",
    ],
)
