# Adame

[![Supported Python versions](https://img.shields.io/pypi/pyversions/Adame.svg)](https://pypi.org/project/v/)
![PyPI](https://img.shields.io/pypi/v/Adame)
![Dependencies](https://img.shields.io/librariesio/github/anionDev/Adame)

[![CodeFactor](https://www.codefactor.io/repository/github/aniondev/Adame/badge/main)](https://www.codefactor.io/repository/github/aniondev/Adame/overview/main)
[![Downloads](https://pepy.tech/badge/adame)](https://pepy.tech/project/adame)
![Coverage](./Adame/Other/Resources/TestCoverageBadges/badge_shieldsio_linecoverage_blue.svg)

![License](https://img.shields.io/badge/license-No_license_available-blue)
![GitHub last commit](https://img.shields.io/github/last-commit/anionDev/Adame)
![GitHub issues](https://img.shields.io/github/issues-raw/anionDev/Adame)

Adame (pronounced: `ăˈ.dam`) is the abbreviation for "Automatic Docker Application Management Engine". So in short: Adame is a tool to manage docker-applications as part in a Linux-environment.

Since adame is usable declarative and is storing data in a [git](https://git-scm.com)-repository Adame is suitable as a application-managing-part of a [GitOps](https://www.weave.works/technologies/gitops)-environment.

## Features

Adame is able to do the following things:

- Generate new application-environment
- Start-/Stop the docker-container according to the configuration-file
- Saves the state of the application inside the docker-container in a git-repository
- Automatically configure a basic intrusion-detection-system for the network-traffic of the docker-container
- Automatically export log-files of the managed application

## Reference

The reference can be found [here](Reference/Index.md).

## Runtime-requirements

Adame is intended to run on Linux-systems.
Furthermore Adame requires that the following commandline-commands are available on your system:

- `chmod` (For setting up permissions on the generated files)
- `chown` (For setting up ownerships on the generated files)
- `docker-compose` >= 1.27.4 (For starting and stopping Docker-container)
- `git` >=2.30.0 (For integrity)
- `gpg` (For checking the integrity of commits)
- `kill` (For killing snort)
- `pip` >= 20.3.1 (On some systems `pip3`)
- `python` >= 3.10 (On some systems `python3`)
- `rsync` (For exporting the log-files to a SIEM-server)
- `ssh` (Required for rsync)
- `snort` (For inspecting the network-traffic of the application)

## Development

### Branching-system

This repository applies the [GitFlowSimplified](https://projects.aniondev.de/Common/Templates/ProjectTemplates/-/blob/main/Templates/Conventions/BranchingSystem/GitFlowSimplified.md)-branching-system.

### Install dependencies

To develop ScriptCollection it is obviously required that the following commandline-commands are available on your system:

- `python` >= 3.10
- `pip3`

The pip-packaged which are required for developing on this project are defined in `requirements.txt`.

Commands like `docker-compose` or `snort` are technically not required for development since these commands will be mocked in the unit-tests.

### IDE

The recommended IDE for developing Adame is Visual Studio Code.
The recommended addons for developing Adame with Visual Studio Code are:

- [Pylance](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-pylance)
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Spell Right](https://marketplace.visualstudio.com/items?itemName=ban.spellright)
- [docs-markdown](https://marketplace.visualstudio.com/items?itemName=docsmsft.docs-markdown)

### Run testcases

To run the testcases simply execute the script stored in `./Reference/Scripts/RunTestcases.script` in the repository's home-directory which is expected to terminate with the exit-code `0`.

### Build

To Create an installable whl-package simply execute `python Setup.py bdist_wheel --dist-dir .`.

## Installation

To install an Adame simply execute `pip install Adame-x.x.x-py3-none-any.whl`.

## TODO-List

- Bug: When running in a different folder (like `adame startadvanced -c someotherfolder/Adame.configuration` then the prescript and postscript may have wrong working-directories.
- Feature: Before starting the docker-container then if a container with same name already exists the already existing container should be stopped and then removed to avoid errors due to already existing container-names.
- Feature: After waiting `maximalexpectedstartduration` seconds there must be a check whether the container is running (and healthy if the health-information is available). If not then an error must be thrown

## License

See `License.txt` for license-information.
