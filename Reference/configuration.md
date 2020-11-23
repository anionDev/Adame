# Configuration

## Adame.configuration

This file is the main configuration-file for an application-environment managed by Adame.

The following configuration-items are available:

TODO

## ApplicationProvidedSecurityInformation.xml

TODO

## Networktraffic.Custom.rules

This is the file where custom application-related rules (typically one rule per line) for the used IDS can be stored in.

`__localipaddress__` can be used in this file as placeholder for the ip-address of the network-interface defined in the file `Adame.configuration`. Adame will automatically replace this placeholder in the file `Networktraffic.Generated.rules` when the configuration will be re-applied.

## LogfilePatterns.txt

TODO

## Security.configuration

TODO

## docker-compose.yml

This file can be edited arbitrarily as long as it satisfies the [specification  for docker-compose-files](https://docs.docker.com/compose/compose-file/) provided by docker.
