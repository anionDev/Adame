# Configuration

## Generated files

When a new repository will be created using the command `Adame create ...` then the following files will be generated:

### Adame.configuration

Typically located in `./TODO`.
This file contains the properties required for Adame itself to manage this repository using [INI-file](https://en.wikipedia.org/wiki/INI_file)-syntax.

### ReadMe.md

Typically located in `.`.
This is a file which should typically be contained on top-level of a [git](https://git-scm.com/)-repository.
This file contains a ReadMe-file with basic information about the repository using [Markdown](https://en.wikipedia.org/wiki/Markdown)-syntax. The user is allowed to arbitrarily edit the content of this file so this file will never be regenerated by Adame after creation.

### License.txt

Typically located in `.`.
This is a file which should typically be contained on top-level of a [git](https://git-scm.com/)-repository.
This file contains the license-information of the repository. The user is allowed to arbitrarily edit the content of this file so this file will never be regenerated by Adame after creation.

### .gitignore

Typically located in `.`.
This is a file which should typically be contained on top-level of a [git](https://git-scm.com/)-repository.
The [gitignore](https://git-scm.com/docs/gitignore)-file contains information about which files should be ignored by [git](https://git-scm.com/) in repository. The user is allowed to arbitrarily edit the content of this file so this file will never be regenerated by Adame after creation.

### ApplicationProvidedSecurityInformation.xml

Typically located in `./TODO`.
This file contains TODO.

### Networktraffic.Generated.rules

Typically located in `./TODO`.
This file contains rules which will be used by the intrusion-detection-system.
Do not edit this file because Adame will overwrite its content.

### Networktraffic.Custom.rules

Typically located in `./TODO`.
This file can contain custom rules which will be used by the intrusion-detection-system. Adame uses this content and adds them together with other rules to `Networktraffic.Generated.rules`.

### LogfilePatterns.txt

Typically located in `./TODO`.
This file contains the patterns to specify/identify the log-files of the application running in the docker-container. The log-files which are matched by this file will be sent to the connected SIEM-system.

### Properties.configuration

Typically located in `./TODO`.
This file contains TODO.

### docker-compose.yml

Typically located in `./TODO`.
The [docker-compose](https://docs.docker.com/compose)-file contains all information for the docker-container to run.