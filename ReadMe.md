# Adame

Adame (pronounced: ăˈ.dam) is the abbreviation for "Automatic Docker Application Management Engine". So in short: Adame is a tool to manage docker-applications as part in a linux-environment.

Since adame is usable declarative and is storing data in a [git](https://git-scm.com)-repository Adame is suitable as a application-managing-part of a [GitOps](https://www.weave.works/technologies/gitops)-environment. 

## Features

Adame is able to do the following things:

- Generate new application-environment
- Start-/Stop the docker-container according to the configuration-file
- Saves the state of the application inside the docker-container in a git-repository
- Automatically configure a basic intrusion-detection-system for the network-traffic of the docker-container
- Automatically export log-files of the managed application

## Reference

The reference can be found [here](Reference/index.md).

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
- `python` >= 3.8.3 (On some systems `python3`)
- `rsync` (For exporting the log-files to a SIEM-server)
- `ssh` (Required for rsync)
- `snort` (For inspecting the network-traffic of the application)

## Development-requirements

### Install dependencies

To develop Adame it is obviously required that the following commandline-commands are available on your system:

- `python` (on some systems `python3`)
- `pip` (on some systems `pip3`)

Commands like `docker-compose` or `snort` are technically not required for development since these commands will be mocked in the unit-tests.

To install all requirements simply execute the script stored in `./Reference/Scripts/InstallDevelopmentDependencies.script`. Every command in this script is expected to terminate with the exit-code `0`

### IDE

The recommended IDE for developing Adame is Visual Studio Code.
The recommended addons for developing Adame with Visual Studio Code are:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python Test Explorer for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=LittleFoxTeam.vscode-python-test-adapter)
- [Spell Right](https://marketplace.visualstudio.com/items?itemName=ban.spellright)
- [docs-markdown](https://marketplace.visualstudio.com/items?itemName=docsmsft.docs-markdown)

### Run testcases

To run the testcases simply execute the script stored in `./Reference/Scripts/RunTestcases.script` in the repository's home-directory which is expected to terminate with the exit-code `0`.

### Build

To create an installable whl-package simply execute the script stored in `./Reference/Scripts/CreateWhlFile.script` in the repository's home-directory which is expected to terminate with the exit-code `0`.

## Installation

To install an Adame simply execute `pip install Adame-1.0.0-py3-none-any.whl`.

## License

See `License.txt` for license-information.
