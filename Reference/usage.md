# Usage

The behavior of all commands (except "create") is idempotent.

## Commands

Adame knows the following commands:

### create

This is the command to create a new Adame-managed environment.

### start

This command ensures that the container is running without modifying anything else.

### stop

This command ensures that the container is not running without modifying anything else.

### applyconfiguration

This command ensures that the current configuration of the Adame-managed environment will be applied (e. g. new firewall-rules).

### run

This command ensures that the docker-application is running with the current configuration. This is the recommended comment which should be executed to keep the application up to date and safe.

Example:

An application is running. Now we configure the environment to use a new version and add a firewall-rule. Then this command combines some of the other commands of Adame: It

- ensures the container is currently not running
- reapllies the configuration defined in the environment
- saves the new state
- ensures that the application will be started again

### save

This command saves the current state of the Docker-container. This command assumes that whenever the docker-container is writing anything into a volume mounted into the docker-container then this is a (part of a) valid state of the application.
