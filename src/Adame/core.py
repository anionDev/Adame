import argparse
from argparse import RawTextHelpFormatter
from ScriptCollection.core import write_message_to_stdout, write_message_to_stderr, write_exception_to_stderr_with_traceback, write_exception_to_stderr, git_commit, execute_and_raise_exception_if_exit_code_is_not_zero, write_text_to_file, ensure_directory_exists, resolve_relative_path_from_current_working_directory
import sys
import traceback
import configparser
import os
from configparser import ConfigParser

version = "0.2.3"
product_name = f"Adame"
adame_with_version = f"{product_name} v{get_adame_version()}"


class AdameCore(object):

    # <constants>

    _private_adame_commit_author_name: str = product_name
    _private_configuration_section_general: str = "general"
    _private_configuration_section_general_key_name: str = "name"
    _private_configuration_section_general_key_owner: str = "owner"
    _private_configuration_section_general_key_gpgkeyofowner: str = "gpgkeyofowner"
    _private_configuration_file: str  # Represents "Adame.configuration" (with folder)
    _private_configuration_folder: str
    _private_security_related_configuration_folder: str
    _private_repository_folder: str
    _private_configuration: ConfigParser

    _private_readme_file: str
    _private_license_file: str
    _private_gitignore_file: str
    _private_dockercompose_file: str
    _private_applicationprovidedsecurityinformation_file: str
    _private_networktrafficgeneratedrules_file: str
    _private_networktrafficcustomrules_file: str
    _private_logfilepatterns_file: str
    _private_propertiesconfiguration_file: str
    # </constants>

    # <properties>

    verbose = False
    encoding = "utf-8"

    # </properties>

    # <initialization>

    def __init__(self):
        pass

    # </initialization>

    # <create_new_environment-command>

    def create_new_environment(self, name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str):
        name = name.replace(" ", "-")
        self._private_verbose_log_start_by_create_command(name, folder, image, owner, gpgkey_of_owner)
        return self._private_execute_task("Create new environment", lambda: self._private_create_new_environment(name, folder, image, owner, gpgkey_of_owner))

    def _private_create_new_environment(self, name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str):
        configuration_file = resolve_relative_path_from_current_working_directory(os.path.join(folder, "Configuration", "Adame.configuration"))

        self._private_create_adame_configuration_file(configuration_file, name, owner, gpgkey_of_owner)
        ensure_directory_exists(self._private_security_related_configuration_folder)

        self._private_create_file_in_repository(self._private_readme_file, self._private_get_readme_file_content(self._private_configuration))
        self._private_create_file_in_repository(self._private_license_file, self._private_get_license_file_content(self._private_configuration))
        self._private_create_file_in_repository(self._private_gitignore_file, self._private_get_gitignore_file_content(self._private_configuration))
        self._private_create_file_in_repository(self._private_dockercompose_file, self._private_get_dockercompose_file_content(image))
        self._private_create_file_in_repository(self._private_applicationprovidedsecurityinformation_file, "")
        self._private_create_file_in_repository(self._private_networktrafficgeneratedrules_file, "")
        self._private_create_file_in_repository(self._private_networktrafficcustomrules_file, "")
        self._private_create_file_in_repository(self._private_logfilepatterns_file, "")
        self._private_create_file_in_repository(self._private_propertiesconfiguration_file, "")

        execute_and_raise_exception_if_exit_code_is_not_zero("git", "init", self._private_repository_folder)
        execute_and_raise_exception_if_exit_code_is_not_zero("git", "config commit.gpgsign true", self._private_repository_folder)
        execute_and_raise_exception_if_exit_code_is_not_zero("git", "config user.signingkey " + gpgkey_of_owner, self._private_repository_folder)

        self._private_commit(self._private_repository_folder, f"Initial commit for Adame app-repository of {name}")
        return 0

    # </create_new_environment-command>

    # <start_environment-command>

    def start_environment(self, configurationfile: str):
        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Start environment", lambda: self._private_start_environment())

    def _private_start_environment(self):
        if(not self._private_container_is_running()):
            self._private_start_container()
        return 0

    # </start_environment-command>

    # <stop_environment-command>

    def stop_environment(self, configurationfile: str):
        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Stop environment", lambda: self._private_stop_environment())

    def _private_stop_environment(self):
        if(self._private_container_is_running()):
            self._private_stop_container()
        return 0

    # </stop_environment-command>

    # <apply_configuration-command>

    def apply_configuration(self, configurationfile: str):
        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Apply configuration", lambda: self._private_apply_configuration())

    def _private_apply_configuration(self):
        self._private_check_integrity_of_repository()
        self._private_regenerate_networktrafficgeneratedrules_filecontent()
        self._private_recreate_siem_connection()
        self._private_recreate_firewall_connection()
        write_message_to_stderr(f"Not implemented yet")
        return 0

    # </apply_configuration-command>

    # <run-command>

    def run(self, configurationfile: str):
        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Run", lambda: self._private_run())

    def _private_run(self):
        self._private_stop_environment()
        self._private_apply_configuration()
        self._private_save()
        self._private_start_environment()
        return 0

    # </run-command>

    # <save-command>

    def save(self, configurationfile: str):
        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Save", lambda: self._private_save())

    def _private_save(self):
        self._private_commit(self._private_repository_folder, f"Saved changes")
        return 0

    # </save-command>

    # <check_integrity-command>

    def check_integrity(self, configurationfile: str):
        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Check integrity", lambda: self._private_check_integrity())

    def _private_check_integrity(self):
        # TODO Implement command
        return 0

    # </check_integrity-command>

    # <helper-functions>

    def _private_check_integrity_of_repository(self):
        """This function checks the integrity of the app-repository.
This function is idempotent."""
        pass  # TODO Implement this function. This function should print/log a warning is the last commit in this repository was not signed with the key defined in the config or if any commit in the last 24*7h (configurable) days was not signed with the key defined in the config because this seems to be an unexpected/unwanted change.

    def _private_regenerate_networktrafficgeneratedrules_filecontent(self):
        """This function regenerates the content of the file Networktraffic.Generated.rules.
This function is idempotent."""
        pass  # TODO Implement this function.

    def _private_recreate_siem_connection(self):
        """This function recreate the SIEM-system-connection.
This function is idempotent."""
        pass  # TODO Implement this function.

    def _private_recreate_firewall_connection(self):
        """This function recreate the connection to the firewall and ensures that the firewall-rules will be applied correctly.
This function is idempotent."""
        pass  # TODO Implement this function.

    def _private_create_adame_configuration_file(self, configuration_file: str, name: str, owner: str, gpgkey_of_owner: str):
        self._private_configuration_file = configuration_file
        ensure_directory_exists(os.path.dirname(self._private_configuration_file))
        configparser = ConfigParser()

        configparser.add_section(self._private_configuration_section_general)
        configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_name] = name
        configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_owner] = owner
        configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_gpgkeyofowner] = gpgkey_of_owner
        with open(self._private_configuration_file, 'w+', encoding=self.encoding) as configfile:
            configparser.write(configfile)
        if(self.verbose):
            write_message_to_stdout(f"Created file '{self._private_configuration_file}'")

        self._private_load_configuration(self._private_configuration_file)

    def _private_verbose_log_start_by_configuration_file(self, configurationfile: str):
        if(self.verbose):
            write_message_to_stdout(f"Started Adame with configurationfile '{configurationfile}'")

    def _private_verbose_log_start_by_create_command(self, name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str):
        if(self.verbose):
            write_message_to_stdout(f"Started Adame with  name='{name}', folder='{folder}', image='{image}', owner='{owner}', gpgkey_of_owner='{gpgkey_of_owner}'")

    def _private_load_configuration(self, configurationfile):
        try:
            self._private_configuration_file = configurationfile
            configuration = configparser.ConfigParser()
            configuration.read(configurationfile)
            self._private_configuration = configuration
            self._private_repository_folder = os.path.dirname(os.path.dirname(configurationfile))
            self._private_configuration_folder = os.path.join(self._private_repository_folder, "Configuration")
            self._private_security_related_configuration_folder = os.path.join(self._private_configuration_folder, "Security")

            _private_readme_file = os.path.join(self._private_repository_folder, "ReadMe.md")
            _private_license_file = os.path.join(self._private_repository_folder, "License.txt")
            _private_gitignore_file = os.path.join(self._private_repository_folder, ".gitignore")
            _private_dockercompose_file = os.path.join(self._private_configuration_folder, "docker-compose.yml")
            _private_applicationprovidedsecurityinformation_file = os.path.join(self._private_security_related_configuration_folder, "ApplicationProvidedSecurityInformation.xml")
            _private_networktrafficgeneratedrules_file = os.path.join(self._private_security_related_configuration_folder, "Networktraffic.Generated.rules")
            _private_networktrafficcustomrules_file = os.path.join(self._private_security_related_configuration_folder, "Networktraffic.Custom.rules")
            _private_logfilepatterns_file = os.path.join(self._private_security_related_configuration_folder, "LogfilePatterns.txt")
            _private_propertiesconfiguration_file = os.path.join(self._private_security_related_configuration_folder, "Properties.configuration")

            return True

        except Exception as exception:
            self._private_handle_exception(exception, f"Error while loading configurationfile '{configurationfile}'.")
            return False

    def _private_get_dockercompose_file_content(self, image: str):
        to_docker_allowed_name = self._private_name_to_docker_allowed_name(self._private_configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_name))
        return f"""version: '3.8'
services:
  {to_docker_allowed_name}:
    image: '{image}'
    container_name: '{to_docker_allowed_name}'
#    ports:
#    volumes:
"""

    def _private_create_file_in_repository(self,  file, filecontent):
        write_text_to_file(file, filecontent, self.encoding)
        if(self.verbose):
            write_message_to_stdout(f"Created file '{file}'")

    def _private_get_license_file_content(self, configuration: ConfigParser):
        return f"""Owner of this repository and its content: {configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_owner)}
Only the owner of this repository is allowed to read, use, change, publish this repository or its content.
Only the owner of this repository is allowed to change the license of this repository or its content.
"""

    def _private_get_gitignore_file_content(self, configuration: ConfigParser):
        return ""

    def _private_get_readme_file_content(self, configuration: ConfigParser):
        return f"""# Purpose

This repository manages the data of the application {configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_name)}.
"""

    def _private_stop_container(self):
        execute_and_raise_exception_if_exit_code_is_not_zero("docker-compose", "down --remove-orphans", self._private_repository_folder)
        # TODO write in certain file the current timestamp and the info that the container was stopped now

    def _private_start_container(self):
        execute_and_raise_exception_if_exit_code_is_not_zero("docker-compose", "up --detach --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps", self._private_repository_folder)
        # TODO write in certain file the current timestamp and the info that the container was started now

    def _private_container_is_running(self):
        write_message_to_stderr(f"Not implemented yet")
        return False  # TODO

    def _private_commit(self, repository: str, message: str):
        commit_id = git_commit(repository, message, self._private_adame_commit_author_name, "")
        if(self.verbose):
            write_message_to_stdout(f"Created commit {commit_id} in repository '{repository}'")

    def _private_execute_task(self, name: str, function):
        try:
            if(self.verbose):
                write_message_to_stdout(f"Started task '{name}'")
            return function()
        except Exception as exception:
            self._private_handle_exception(exception, f"Exception occurred in task '{name}'")
            return 2
        finally:
            if(self.verbose):
                write_message_to_stdout(f"Finished task '{name}'")

    def _private_handle_exception(self, exception: Exception, message: str):
        if(self.verbose):
            write_exception_to_stderr_with_traceback(exception, traceback, message)
        else:
            write_exception_to_stderr(exception, message)

    def _private_name_to_docker_allowed_name(self, name: str):
        name = name.lower()
        return name

    # </helper-functions>

# <commands>


def create_new_environment(name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.create_new_environment(name, folder, image, gpgkey_of_owner, owner)


def start_environment(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.start_environment(configuration_file)


def stop_environment(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.stop_environment(configuration_file)


def apply_configuration(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.apply_configuration(configuration_file)


def run(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.run(configuration_file)


def save(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.save(configuration_file)


def check_integrity(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.check_integrity(configuration_file)

# </commands>

# <miscellaneous>


def get_adame_version():
    return version


def adame_cli():
    arger = argparse.ArgumentParser(description=f"""{adame_with_version}
Adame (Automatic Docker Application Management Engine) is a tool which manages (install, start, stop) docker-applications.
One focus of Adame is to store the state of an application: Adame stores all data of the application in git-repositories. So with Adame it is very easy move the application with all its data and configurations to another computer.
Another focus of Adame is it-forensics and it-security: Adame generates a basic snort-configuration for each application to detect/log/bloock networktraffic from the docker-container of the application which is obvious harmful.

Required commandline-commands:
-docker-compose
-git
-gpg
-snort""", formatter_class=RawTextHelpFormatter)

    arger.add_argument("--verbose", action="store_true")

    subparsers = arger.add_subparsers(dest="command")

    create_command_name = "create"
    create_parser = subparsers.add_parser(create_command_name)
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--folder", required=True)
    create_parser.add_argument("--image", required=True)
    create_parser.add_argument("--owner", required=True)
    create_parser.add_argument("--gpgkey_of_owner", required=True)

    start_command_name = "start"
    start_parser = subparsers.add_parser(start_command_name)
    start_parser.add_argument("--configurationfile", required=True)

    stop_command_name = "stop"
    stop_parser = subparsers.add_parser(stop_command_name)
    stop_parser.add_argument("--configurationfile", required=True)

    apply_configuration_command_name = "applyconfiguration"
    apply_configuration_parser = subparsers.add_parser(apply_configuration_command_name)
    apply_configuration_parser.add_argument("--configurationfile", required=True)

    run_command_name = "run"
    run_parser = subparsers.add_parser(run_command_name)
    run_parser.add_argument("--configurationfile", required=True)

    save_command_name = "save"
    save_parser = subparsers.add_parser(run_command_name)
    save_parser.add_argument("--configurationfile", required=True)

    check_integrity_command_name = "checkintegrity"
    check_integrity_parser = subparsers.add_parser(run_command_name)
    check_integrity_parser.add_argument("--configurationfile", required=True)

    options = arger.parse_args()
    verbose = options.verbose
    if options.command == create_command_name:
        return create_new_environment(options.name, options.folder, options.image, options.owner, options.gpgkey_of_owner, verbose)
    elif options.command == start_command_name:
        return start_environment(options.configurationfile, verbose)
    elif options.command == stop_command_name:
        return stop_environment(options.configurationfile, verbose)
    elif options.command == apply_configuration_command_name:
        return apply_configuration(options.configurationfile, verbose)
    elif options.command == run_command_name:
        return run(options.configurationfile, verbose)
    elif options.command == save_command_name:
        return save(options.configurationfile, verbose)
    elif options.command == check_integrity_command_name:
        return check_integrity(options.configurationfile, verbose)
    else:
        if options.command == None:
            write_message_to_stdout(adame_with_version)
            write_message_to_stdout(f"Run '{product_name} --help' to get help about the usage.")
            return 0
        else:
            write_message_to_stdout(f"Unknown command: '{options.command}'")
            return 1

# </miscellaneous>
