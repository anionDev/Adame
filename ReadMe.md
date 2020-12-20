# General

Adame: Automatic Docker Application Management Engine

Adame is a tool to manage docker-applications.

## Features

Adame is able to do the following things:

- Generate new application-environment
- Start-/Stop the docker-container according to the configuration-file
- Saves the state of the application inside the docker-container in a git-repository
- Automatically configure a basic intrusion-detection-system for the network-traffic of the docker-container

## Reference

The reference can be found [here](Reference/index.md).

## Runtime-requirements

Adame is intended to run on Linux-systems.
Furthermore Adame requires that the following commandline-commands are available on your system:

- `chmod` (For setting up some permissions on the generated files)
- `docker-compose` (For starting and stopping Docker-container)
- `git` (For integrity)
- `gpg` (For checking the integrity of commits)
- `kill` (For killing snort)
- `pip` (On some systems `pip3`)
- `python` (On some systems `python3`)
- `rsync` (For exporting the log-files to a SIEM-server)
- `ssh` (Required for rsync)
- `snort` (For inspecting the network-traffic of the application)

## Development-requirements

### Install dependencies

To develop Adame it is obviously required that the following commandline-commands are available on your system:

- `python` (on some systems `python3`)
- `pip` (on some systems `pip3`)

Commands like `docker-compose` or `snort` are technically not required for development since these commands will be mocked in the unit-tests.

To install all requirements simply execute the script stored in `./Reference/Scripts/InstallDevelopmentDependencies.script`. Every command in this script is expected to terminate with the exitcode `0`


### IDE

The recommended IDE for developing Adame is Visual Studio Code.
The recommended addons for developing Adame with Visual Studio Code are:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python Test Explorer for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=LittleFoxTeam.vscode-python-test-adapter)
- [Spell Right](https://marketplace.visualstudio.com/items?itemName=ban.spellright)
- [docs-markdown](https://marketplace.visualstudio.com/items?itemName=docsmsft.docs-markdown)

### Run testcases

To run the testcases simply execute the script stored in `./Reference/Scripts/CreateWhlFile` in the repository's home-directory which is expected to terminate with the exitcode `0`.

### Build

To create an installable whl-package simply execute the script stored in `./Reference/Scripts/CreateWhlFile` in the repository's home-directory which is expected to terminate with the exitcode `0`.

## Installation

To install an Adame simply execute `pip install Adame-1.0.0-py3-none-any.whl`.

## License

See `License.txt` for license-information.
