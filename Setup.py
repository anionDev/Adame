import os
from setuptools import setup

version = "1.2.18"


def create_wheel_file():

    productname = "Adame"

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
            "Programming Language :: Python :: 3.9",
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
            "netifaces>=0.11",
            "packaging>=21.3",
            "psutil>=5.9.0",
            "ScriptCollection>=2.8.4",
        ],
        entry_points={
            'console_scripts': [
                f"adame = {productname}.{productname}:adame_cli"
            ],
        },
    )


create_wheel_file()
