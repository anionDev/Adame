<!-- markdownlint-disable MD024 -->

# Usage

The behavior of all commands (except `create`) is idempotent.

Caution:

- The commands are not intended to be executed in an unattended script since it is recommended to enable gpg-signing which contains the user-interaction of the pinentry-dialog.
- Adame requires elevated privileges for executing commands like snort or docker-compose.

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

This command ensures that the container is not running anymore without modifying anything else.
This command saves the current state of the Docker-container. This command assumes that whenever the docker-container is writing anything into a volume mounted into the docker-container then this is a (part of a) valid state of the application.

### applyconfiguration

#### Syntax

`Adame applyconfiguration --configurationfile Adame.configuration`

#### Description

This command ensures that the current configuration of the Adame-managed environment will be applied (e. g. new rules for the intrusion detection system).

### diagnosis

#### Syntax

`Adame diagnosis --configurationfile Adame.configuration`

#### Description

The purpose of this command is to help and give information when something is not working correctly as expected.

### startadvanced

#### Syntax

`Adame startadvanced --configurationfile Adame.configuration`

#### Description

This command ensures that the docker-application is running with the current configuration. This is the recommended comment which should be executed to keep the application up to date and safe.

Example:

An application is running. Now we configure the environment to use a new version and add a rule for the intrusion detection system. Then this command combines some of the other commands of Adame: It

- ensures the container is currently not running
- re-applies the configuration defined in the environment
- saves the current state
- ensures that the application will be started again

### stopadvanced

#### Syntax

`Adame stopadvanced --configurationfile Adame.configuration`

#### Description

Tops the container and saves the current state of the repository.
