from setuptools import setup


setup(
    name="jobsqueue",
    version="0.5",
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
