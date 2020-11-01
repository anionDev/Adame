# Adame

Adame: Automatic Docker Application Management Engine

Adame is a tool to manage docker-applications.

# Features

Adame is able to do the following things:
- Generate new configuration-file for container
- Create docker-container according to the configuration-file
- Start-/Stop the docker-container according to the configuration-file
- Saves the state of the application inside the docker-container in a git-repository
- Automatically installs a basic intrusion-detection-system for the network-traffic of the docker-container

# Requirements

Adame is intended to run on linux-systems.
Furthermore Adame requires that the following commandline-commands are available on your system:
-python
-docker-compose
-git
-snort

# Installation

```
pip install Adame.whl
```

# Reference

The reference can be found [here](Reference/index.md);


# License

No license available yet.
