from setuptools import setup, find_packages
import os

productname = "Adame"
version = "0.2.1"

with open(f"..{os.path.sep}ReadMe.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=productname,
    version=version,
    description=f"Adame (Automatic Docker Application Management Engine) is a tool which manages (install, start, stop) docker-applications.",
    packages=[productname],
    author='Marius Göcke',
    author_email='marius.goecke@gmail.com',
    url='https://notavailableyet',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Topic :: System :: Logging",
        "Topic :: System :: Monitoring",
        "Topic :: Terminals"
    ],
    platforms=["windows10", "linux"],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        "ScriptCollection==1.3.3",
    ],
    entry_points={
        'console_scripts': [
            f"adame = adame:adame_cli"
        ],
    },
)
