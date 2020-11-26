import os
from setuptools import setup

productname = "Adame"
version = "0.4.3"


folder_of_current_file = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(folder_of_current_file, "ReadMe.md"), "r", encoding='utf-8') as file:
    long_description = file.read()

setup(
    name=productname,
    version=version,
    description="Adame (Automatic Docker Application Management Engine) is a tool which manages (install, start, stop) docker-applications.",
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
        "netifaces>=0.10.9",
        "psutil>=5.7.3",
        "ScriptCollection>=2.0.12",
    ],
    entry_points={
        'console_scripts': [
            "adame = Adame.core:adame_cli"
        ],
    },
)
