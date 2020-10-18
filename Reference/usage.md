<!-- markdownlint-disable MD024 -->

# Usage

The behavior of all commands (except `create`) is idempotent.

Caution: The commands are not intended to be executed in an unattended script since it contains user-interaction (gpg-pinentry).

## Commands

Adame knows the following commands:

### create

#### Syntax

`Adame create --name MyApplicationName --folder /MyFolder --image MyImage:latest --owner MyName`

#### Description

This is the command to create a new Adame-managed environment. Technically this is implemented as new git-repository.

### start

#### Syntax

`Adame start --configurationfile Adame.configuration`

#### Description

This command ensures that the container is running without modifying anything else.

### stop

#### Syntax

`Adame stop --configurationfile Adame.configuration`

#### Description

This command ensures that the container is not running without modifying anything else.

### applyconfiguration

#### Syntax

`Adame applyconfiguration --configurationfile Adame.configuration`

#### Description

This command ensures that the current configuration of the Adame-managed environment will be applied (e. g. new firewall-rules).

### run

#### Syntax

`Adame run --configurationfile Adame.configuration`

#### Description

This command ensures that the docker-application is running with the current configuration. This is the recommended comment which should be executed to keep the application up to date and safe.

Example:

An application is running. Now we configure the environment to use a new version and add a firewall-rule. Then this command combines some of the other commands of Adame: It

- ensures the container is currently not running
- reapllies the configuration defined in the environment
- saves the current state
- ensures that the application will be started again


### save

#### Syntax

`Adame save --configurationfile Adame.configuration`

#### Description

This command saves the current state of the Docker-container. This command assumes that whenever the docker-container is writing anything into a volume mounted into the docker-container then this is a (part of a) valid state of the application.

