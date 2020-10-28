from setuptools import setup
import os
from pathlib import Path

productname = "Adame"
version = "0.2.13"


folder_of_current_file = os.path.dirname(os.path.realpath(__file__))
with open(str(Path(os.path.join(folder_of_current_file, f".{os.sep}ReadMe.md")).resolve()), "r", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=productname,
    version=version,
    description=f"Adame (Automatic Docker Application Management Engine) is a tool which manages (install, start, stop) docker-applications.",
    packages=[productname],
    author='Marius Göcke',
    author_email='marius.goecke@gmail.com',
    url='https://not.available.yet',
    license='None',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "Topic :: Terminals"
    ],
    platforms=["linux"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "ScriptCollection>=1.12.45",
    ],
    entry_points={
        'console_scripts': [
            f"adame = Adame.core:adame_cli"
        ],
    },
)
