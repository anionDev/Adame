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

- `docker-compose`
- `git`
- `kill`
- `pip` (on some systems `pip3`)
- `python` (on some systems `python3`)
- `snort`

## Development-requirements

### Install dependencies

To develop Adame it is obviously required that the following commandline-commands are available on your system:

- `python` (on some systems `python3`)
- `pip` (on some systems `pip3`)

Commands like `docker-compose` or `snort` are technically not required for development since these commands will be mocked in the unit-tests.

To install all required pip-packages simply execute the following commands:

```lang-bash
pip install "netifaces>=0.10.9"
pip install "psutil>=5.7.3"
pip install "pylint>=2.6.0"
pip install "pytest>=6.1.2"
pip install "ScriptCollection>=2.0.15"
pip install "wheel>=0.35.1"
```

### IDE

The recommended IDE for developing Adame is Visual Studio Code.
The recommended addons for developing Adame with Visual Studio Code are:

- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
- [Python Test Explorer for Visual Studio Code](https://marketplace.visualstudio.com/items?itemName=LittleFoxTeam.vscode-python-test-adapter)
- [Spell Right](https://marketplace.visualstudio.com/items?itemName=ban.spellright)
- [docs-markdown](https://marketplace.visualstudio.com/items?itemName=docsmsft.docs-markdown)

### Build

To Create an installable whl-package simply execute `python Setup.py bdist_wheel --dist-dir .`.

## Installation

To install an Adame simply execute `pip install Adame-1.0.0-py3-none-any.whl`.

## License

See `License.txt` for license-information.
