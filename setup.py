import setuptools

import versioneer

setuptools.setup(
    name="jobsqueue",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="André Graça",
    author_email="andre.p.g@sapo.pt",
    description="Job manager that can be shared by multiple users to programatically run commands with different priority levels.",
    packages=setuptools.find_packages(),
    python_requires="3.7",
    install_requires=["pandas", "easydict", "gpustat", "filelock", "versioneer"],
)
