import argparse
import socket
from argparse import RawTextHelpFormatter
from ScriptCollection.core import file_is_empty, folder_is_empty, str_none_safe, ensure_file_exists, git_add_or_set_remote_address, git_push, write_message_to_stdout, write_message_to_stderr, write_exception_to_stderr_with_traceback, write_exception_to_stderr, git_commit, execute_and_raise_exception_if_exit_code_is_not_zero, write_text_to_file, ensure_directory_exists, resolve_relative_path_from_current_working_directory, string_is_none_or_whitespace, string_has_nonwhitespace_content
import sys
import traceback
import configparser
import os
from datetime import datetime
from configparser import ConfigParser
import time
import datetime

version = "0.2.12"
product_name = "Adame"
adame_with_version = f"{product_name} v{version}"


class AdameCore(object):

    # <constants>

    _private_adame_commit_author_name: str = product_name
    _private_configuration_section_general: str = "general"
    _private_configuration_section_general_key_name: str = "name"
    _private_configuration_section_general_key_owner: str = "owner"
    _private_configuration_section_general_key_gpgkeyofowner: str = "gpgkeyofowner"
    _private_configuration_section_general_key_remoteaddress: str = "remoteaddress"
    _private_configuration_file: str  # Represents "Adame.configuration" (with folder)
    _private_configuration_folder: str
    _private_security_related_configuration_folder: str
    _private_repository_folder: str
    _private_configuration: ConfigParser
    _private_log_folder: str = "Logs"
    _private_log_folder_for_internal_overhead: str = os.path.join(_private_log_folder, "Overhead")
    _private_log_folder_for_application: str = os.path.join(_private_log_folder, "Application")
    _private_log_file_for_adame_overhead: str

    _private_readme_file: str
    _private_license_file: str
    _private_gitignore_file: str
    _private_dockercompose_file: str
    _private_applicationprovidedsecurityinformation_file: str
    _private_networktrafficgeneratedrules_file: str
    _private_networktrafficcustomrules_file: str
    _private_logfilepatterns_file: str
    _private_propertiesconfiguration_file: str

    _private_gpgkey_of_owner_is_available: bool
    _private_remote_address_is_available: bool

    # </constants>

    # <properties>

    verbose = False
    encoding = "utf-8"

    # </properties>

    # <initialization>

    def __init__(self):
        pass

    # </initialization>

    # <create-command>

    def create(self, name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str = None, remote_address: str = None):

        self._private_verbose_log_start_by_create_command(name, folder, image, owner)
        return self._private_execute_task("Create", lambda: self._private_create(name, folder, image, owner, gpgkey_of_owner, remote_address))

    def _private_create(self, name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str, remote_address: str = ""):

        if name is None:
            raise Exception("Argument 'name' is not defined")
        else:
            name = name.replace(" ", "-")

        if folder is None:
            raise Exception("Argument 'folder' is not defined")
        else:
            if(os.path.isdir(folder) and not folder_is_empty(folder)):
                raise Exception(f"Folder '{folder}' does already have content")
            else:
                ensure_directory_exists(folder)

        if image is None:
            raise Exception("Argument 'image' is not defined")

        if owner is None:
            raise Exception("Argument 'owner' is not defined")

        if gpgkey_of_owner is None:
            gpgkey_of_owner = ""

        if remote_address is None:
            remote_address = ""
        configuration_file = resolve_relative_path_from_current_working_directory(os.path.join(folder, "Configuration", "Adame.configuration"))

        if self._private_create_adame_configuration_file(configuration_file, name, owner, gpgkey_of_owner, remote_address) != 0:
            return 1

        ensure_directory_exists(self._private_security_related_configuration_folder)

        self._private_create_file_in_repository(self._private_readme_file, self._private_get_readme_file_content(self._private_configuration, image))
        self._private_create_file_in_repository(self._private_license_file, self._private_get_license_file_content(self._private_configuration))
        self._private_create_file_in_repository(self._private_gitignore_file, self._private_get_gitignore_file_content(self._private_configuration))
        self._private_create_file_in_repository(self._private_dockercompose_file, self._private_get_dockercompose_file_content(image))
        self._private_create_file_in_repository(self._private_applicationprovidedsecurityinformation_file, "")
        self._private_create_file_in_repository(self._private_networktrafficgeneratedrules_file, "")
        self._private_create_file_in_repository(self._private_networktrafficcustomrules_file, "")
        self._private_create_file_in_repository(self._private_logfilepatterns_file, "")
        self._private_create_file_in_repository(self._private_propertiesconfiguration_file, "")

        execute_and_raise_exception_if_exit_code_is_not_zero("git", "init", self._private_repository_folder)
        if self._private_gpgkey_of_owner_is_available:
            execute_and_raise_exception_if_exit_code_is_not_zero("git", "config commit.gpgsign true", self._private_repository_folder)
            execute_and_raise_exception_if_exit_code_is_not_zero("git", "config user.signingkey " + gpgkey_of_owner, self._private_repository_folder)

        self._private_commit(self._private_repository_folder, f"Initial commit for Adame app-repository of {name} in folder '{self._private_repository_folder}' on host '{socket.gethostname()}'")
        return 0

    # </create-command>

    # <start-command>

    def start(self, configurationfile: str):

        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Start environment", lambda: self._private_start())

    def _private_start(self):
        if(not self._private_container_is_running()):
            self._private_start_container()
            self._private_ensure_intrusion_detection_is_running()
        return 0

    # </start-command>

    # <stop-command>

    def stop(self, configurationfile: str):

        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Stop environment", lambda: self._private_stop())

    def _private_stop(self):
        if(self._private_container_is_running()):
            self._private_stop_container()
            self._private_ensure_intrusion_detection_is_not_running()
        return 0

    # </stop>

    # <applyconfiguration-command>

    def applyconfiguration(self, configurationfile: str):

        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Apply configuration", lambda: self._private_applyconfiguration())

    def _private_applyconfiguration(self):
        self._private_check_integrity_of_repository()
        self._private_regenerate_networktrafficgeneratedrules_filecontent()
        self._private_recreate_siem_connection()
        self._private_commit(self._private_repository_folder, f"Reapplied configuration")
        return 0

    # </applyconfiguration-command>

    # <startadvanced-command>

    def startadvanced(self, configurationfile: str):

        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("StartAdvanced", lambda: self._private_startadvanced())

    def _private_startadvanced(self):
        self._private_stopadvanced()
        self._private_applyconfiguration()
        self._private_start()
        return 0

    # </startadvanced-command>

    # <stopadvanced-command>

    def stopadvanced(self, configurationfile: str):

        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("StopAdvanced", lambda: self._private_stopadvanced())

    def _private_stopadvanced(self):
        self._private_stop()
        self._private_commit(self._private_repository_folder, f"Saved changes")
        return 0

    # </stopadvanced-command>

    # <checkintegrity-command>

    def checkintegrity(self, configurationfile: str):

        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if self._private_load_configuration(configurationfile) != 0:
            return 1
        return self._private_execute_task("Check integrity", lambda: self._private_checkintegrity())

    def _private_checkintegrity(self):
        self._private_check_integrity_of_repository(7)
        return 0

    # </checkintegrity-command>

    # <diagnosis-command>

    def diagnosis(self, configurationfile: str):

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if configurationfile is not None:
            if self._private_load_configuration(configurationfile) != 0:
                return 1
        return self._private_execute_task("Diagnosis", lambda: self._private_diagnosis())

    def _private_diagnosis(self):
        if self._private_adame_general_diagonisis() != 0:
            return 1
        if self._private_configuration is not None:
            if self._private_adame_repository_diagonisis() != 0:
                return 1
        return 0

    # </checkintegrity-command>

    # <helper-functions>

    def _private_adame_general_diagonisis(self):
        pass  # TODO implement function

    def _private_adame_repository_diagonisis(self):
        pass  # TODO implement function

    def _private_check_configurationfile_argument(self, configurationfile: str):
        if configurationfile is None:
            raise Exception("Argument 'configurationfile' is not defined")

    def _private_check_integrity_of_repository(self, amount_of_days_of_history_to_check: int = None):
        """This function checks the integrity of the app-repository.
This function is idempotent."""
        # until = datetime.datetime.today()
        # since = until - datetime.timedelta(days=amount_of_days_of_history_to_check)
        # commit_hashs_to_check_in_given_interval = self._private_get_commit_ids_between_dates(until, since)
        pass  # TODO Implement this function. This function should print a warning is the last commit in this repository was not signed with the key defined in the config or if any commit in the last amount_of_days_of_history_to_check days (configurable) days was not signed with the key defined in the config because this seems to be an unexpected/unwanted change.

    def _private_regenerate_networktrafficgeneratedrules_filecontent(self):
        """This function regenerates the content of the file Networktraffic.Generated.rules.
This function is idempotent."""
        pass  # TODO This function must
        # - process ApplicationProvidedSecurityInformation.xml
        # - add a testrule for _private_test_intrusion_detection()
        # - add the rules from Networktraffic.Custom.rules

    def _private_recreate_siem_connection(self):
        """This function recreate the SIEM-system-connection.
This function is idempotent."""
        pass  # TODO Implement this function.

    def _private_ensure_intrusion_detection_is_running(self):
        """This function ensures that the intrusion-detection-system is running and the rules will be applied correctly.
This function is idempotent."""
        if(not self._private_intrusion_detection_is_running()):
            self._private_stop_intrusion_detection()
        self._private_start_intrusion_detection()
        self._private_test_intrusion_detection()

    def _private_ensure_intrusion_detection_is_not_running(self):
        """This function ensures that the intrusion-detection-system is not running anymore.
This function is idempotent."""
        if(self._private_intrusion_detection_is_running()):
            self._private_stop_intrusion_detection()

    def _private_intrusion_detection_is_running(self):
        pass  # TODO return true if and only if the intrusion-detection-system (which was started by self._private_start_intrusion_detection()) is running

    def _private_start_intrusion_detection(self):
        pass  # TODO start the intrusion-detection-system as daemon

    def _private_stop_intrusion_detection(self):
        pass  # TODO stop a intrusion-detection-system (which was started by self._private_start_intrusion_detection())

    def _private_test_intrusion_detection(self):
        pass  # TODO test if a specific test-rule will be applied by sending a package to the docker-container which should be detected by the instruction-detection-system

    def _private_create_adame_configuration_file(self, configuration_file: str, name: str, owner: str, gpgkey_of_owner: str, remote_address: str):
        self._private_configuration_file = configuration_file
        ensure_directory_exists(os.path.dirname(self._private_configuration_file))
        configparser = ConfigParser()

        configparser.add_section(self._private_configuration_section_general)
        configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_name] = name
        configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_owner] = owner
        configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_gpgkeyofowner] = gpgkey_of_owner
        configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_remoteaddress] = remote_address

        with open(self._private_configuration_file, 'w+', encoding=self.encoding) as configfile:
            configparser.write(configfile)
        self._private_log_information(f"Created file '{self._private_configuration_file}'", True)

        return self._private_load_configuration(self._private_configuration_file)

    def _private_verbose_log_start_by_configuration_file(self, configurationfile: str):
        self._private_log_information(f"Started Adame with configurationfile '{configurationfile}'", True)

    def _private_verbose_log_start_by_create_command(self, name: str, folder: str, image: str, owner: str):
        self._private_log_information(f"Started Adame with  name='{str_none_safe(name)}', folder='{str_none_safe(folder)}', image='{str_none_safe(image)}', owner='{str_none_safe(owner)}'", True)

    def _private_load_configuration(self, configurationfile):
        try:
            self._private_configuration_file = configurationfile
            configuration = configparser.ConfigParser()
            configuration.read(configurationfile)
            self._private_configuration = configuration
            self._private_repository_folder = os.path.dirname(os.path.dirname(configurationfile))
            self._private_configuration_folder = os.path.join(self._private_repository_folder, "Configuration")
            self._private_security_related_configuration_folder = os.path.join(self._private_configuration_folder, "Security")

            self._private_readme_file = os.path.join(self._private_repository_folder, "ReadMe.md")
            self._private_license_file = os.path.join(self._private_repository_folder, "License.txt")
            self._private_gitignore_file = os.path.join(self._private_repository_folder, ".gitignore")
            self._private_dockercompose_file = os.path.join(self._private_configuration_folder, "docker-compose.yml")
            self._private_applicationprovidedsecurityinformation_file = os.path.join(self._private_security_related_configuration_folder, "ApplicationProvidedSecurityInformation.xml")
            self._private_networktrafficgeneratedrules_file = os.path.join(self._private_security_related_configuration_folder, "Networktraffic.Generated.rules")
            self._private_networktrafficcustomrules_file = os.path.join(self._private_security_related_configuration_folder, "Networktraffic.Custom.rules")
            self._private_logfilepatterns_file = os.path.join(self._private_security_related_configuration_folder, "LogfilePatterns.txt")
            self._private_propertiesconfiguration_file = os.path.join(self._private_security_related_configuration_folder, "Properties.configuration")

            self._private_log_folder: str = os.path.join(self._private_repository_folder, "Logs")
            self._private_log_folder_for_internal_overhead: str = os.path.join(self._private_log_folder, "Overhead")
            self._private_log_folder_for_application: str = os.path.join(self._private_log_folder, "Application")

            ensure_directory_exists(self._private_log_folder_for_internal_overhead)
            ensure_directory_exists(self._private_log_folder_for_application)
            self._private_log_file_for_adame_overhead: str = os.path.join(self._private_log_folder_for_internal_overhead, "Adame.log")

            self._private_gpgkey_of_owner_is_available = string_has_nonwhitespace_content(self._private_configuration[self._private_configuration_section_general][self._private_configuration_section_general_key_gpgkeyofowner])
            self._private_remote_address_is_available = string_has_nonwhitespace_content(self._private_configuration[self._private_configuration_section_general][self._private_configuration_section_general_key_remoteaddress])

            if(not self._private_gpgkey_of_owner_is_available):
                self._private_log_information(f"Warning: GPGKey of the owner of the repository is not set. It is highly recommended to set this value to ensure the integrity of the app-repository.")
            if(not self._private_remote_address_is_available):
                self._private_log_information(f"Warning: Remote-address of the repository is not set. It is highly recommended to set this value to save the content of the app-repository externally.")

            return 0

        except Exception as exception:
            self._private_log_exception(f"Error while loading configurationfile '{configurationfile}'.", exception)
            return 1

    def _private_get_dockercompose_file_content(self, image: str):
        name_as_docker_allowed_name = self._private_name_to_docker_allowed_name(self._private_configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_name))
        return f"""version: '3.8'
services:
  {name_as_docker_allowed_name}:
    image: '{image}'
    container_name: '{name_as_docker_allowed_name}'
#     ports:
#     volumes:
"""

    def _private_create_file_in_repository(self,  file, filecontent):
        write_text_to_file(file, filecontent, self.encoding)
        self._private_log_information(f"Created file '{file}'", True)

    def _private_get_license_file_content(self, configuration: ConfigParser):
        return f"""Owner of this repository and its content: {configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_owner)}
Only the owner of this repository is allowed to read, use, change, publish this repository or its content.
Only the owner of this repository is allowed to change the license of this repository or its content.
"""

    def _private_get_gitignore_file_content(self, configuration: ConfigParser):
        return """Logs/**
"""

    def _private_get_readme_file_content(self, configuration: ConfigParser, image: str):

        if self._private_remote_address_is_available:
            remote_address_info = f"The data of this repository will be saved as backup in '{configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_remoteaddress)}'."
        else:
            remote_address_info = "Currently there is no backup-address defined for backups of this repository."

        if self._private_gpgkey_of_owner_is_available:
            gpgkey_of_owner_info = f"The integrity of the data of this repository will ensured using the GPG-key {configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_gpgkeyofowner)}."
        else:
            gpgkey_of_owner_info = "Currently there is no GPG-key defined to ensure the integrity of this repository."

        return f"""# Purpose

This repository manages the data of the application {configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_name)}.

# Technical information

# Image

The docker-image {image} will be used.

# Backup

{remote_address_info}

# Integrity

{gpgkey_of_owner_info}

# License

The license of this repository is defined in the file 'License.txt'.

"""

    def _private_stop_container(self):
        execute_and_raise_exception_if_exit_code_is_not_zero("docker-compose", "down --remove-orphans", self._private_repository_folder)
        self._private_log_information("Container was stopped", False, True, True)

    def _private_start_container(self):
        execute_and_raise_exception_if_exit_code_is_not_zero("docker-compose", "up --detach --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps", self._private_repository_folder)
        self._private_log_information("Container was started", False, True, True)

    def _private_container_is_running(self):
        return False  # TODO

    def _private_commit(self, repository: str, message: str):
        commit_id = git_commit(repository, message, self._private_adame_commit_author_name, "")
        remote_name = "Backup"
        branch_name = "master"
        remote_address = self._private_configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_remoteaddress)
        self._private_log_information(f"Created commit {commit_id} ('{message}') in repository '{repository}'", False, True, True)
        if self._private_remote_address_is_available:
            git_add_or_set_remote_address(self._private_repository_folder, remote_name, remote_address)
            git_push(self._private_repository_folder, remote_name, branch_name, branch_name, False, False)
            self._private_log_information(f"Pushed repository '{repository}' to remote {remote_address}", False, True, True)

    def _private_name_to_docker_allowed_name(self, name: str):
        name = name.lower()
        return name

    def _private_execute_task(self, name: str, function):
        try:
            self._private_log_information(f"Started task '{name}'")
            return function()
        except Exception as exception:
            self._private_log_exception(f"Exception occurred in task '{name}'", exception)
            return 2
        finally:
            self._private_log_information(f"Finished task '{name}'")

    def _private_log_information(self, message: str, is_verbose_log_entry: bool = False, write_to_console: bool = True, write_to_logfile: bool = False):
        self._private_write_to_log("Information", message, is_verbose_log_entry, write_to_console, write_to_logfile)

    def _private_log_warning(self, message: str, is_verbose_log_entry: bool = False, write_to_console: bool = True, write_to_logfile: bool = False):
        self._private_write_to_log("Warning", message, is_verbose_log_entry, write_to_console, write_to_logfile)

    def _private_log_error(self, message: str, is_verbose_log_entry: bool = False, write_to_console: bool = True, write_to_logfile: bool = False):
        self._private_write_to_log("Error", message, is_verbose_log_entry, write_to_console, write_to_logfile)

    def _private_log_exception(self, message: str, exception: Exception, is_verbose_log_entry: bool = False, write_to_console: bool = True, write_to_logfile: bool = False):
        self._private_write_to_log("Error", f"{message}; {str(exception)}", is_verbose_log_entry, write_to_console, write_to_logfile)
        if(self.verbose):
            write_exception_to_stderr_with_traceback(exception, traceback, message)

    def _private_write_to_log(self, loglevel: str, message: str, is_verbose_log_entry: bool, write_to_console: bool, write_to_logfile: bool):
        if is_verbose_log_entry and not self.verbose:
            return
        timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        logentry = f"[{timestamp}] [{loglevel}] {message}"
        if(write_to_console):
            if(loglevel == "Error"):
                write_message_to_stderr(logentry)
            else:
                write_message_to_stdout(logentry)
        if(write_to_logfile and self._private_log_file_for_adame_overhead is not None):
            ensure_file_exists(self._private_log_file_for_adame_overhead)
            if file_is_empty(self._private_log_file_for_adame_overhead):
                prefix = ''
            else:
                prefix = '\n'
            with open(self._private_log_file_for_adame_overhead, "a") as file:
                file.write(prefix+logentry)

    # </helper-functions>

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

    arger.add_argument("--verbose", action="store_true", required=False)

    subparsers = arger.add_subparsers(dest="command")

    create_command_name = "create"
    create_parser = subparsers.add_parser(create_command_name)
    create_parser.add_argument("--name", required=True)
    create_parser.add_argument("--folder", required=True)
    create_parser.add_argument("--image", required=True)
    create_parser.add_argument("--owner", required=True)
    create_parser.add_argument("--gpgkey_of_owner", required=False)
    create_parser.add_argument("--remote_address", required=False)

    start_command_name = "start"
    start_parser = subparsers.add_parser(start_command_name)
    start_parser.add_argument("--configurationfile", required=True)

    stop_command_name = "stop"
    stop_parser = subparsers.add_parser(stop_command_name)
    stop_parser.add_argument("--configurationfile", required=True)

    apply_configuration_command_name = "applyconfiguration"
    apply_configuration_parser = subparsers.add_parser(apply_configuration_command_name)
    apply_configuration_parser.add_argument("--configurationfile", required=True)

    startadvanced_command_name = "startadvanced"
    startadvanced_parser = subparsers.add_parser(startadvanced_command_name)
    startadvanced_parser.add_argument("--configurationfile", required=True)

    stopadvanced_command_name = "stopadvanced"
    stopadvanced_parser = subparsers.add_parser(stopadvanced_command_name)
    stopadvanced_parser.add_argument("--configurationfile", required=True)

    checkintegrity_command_name = "checkintegrity"
    checkintegrity_parser = subparsers.add_parser(checkintegrity_command_name)
    checkintegrity_parser.add_argument("--configurationfile", required=True)

    diagnosis_command_name = "diagnosis"
    diagnosis_parser = subparsers.add_parser(diagnosis_command_name)
    diagnosis_parser.add_argument("--configurationfile", required=False)

    options = arger.parse_args()

    core = AdameCore()
    core.verbose = options.verbose

    if options.command == create_command_name:
        return core.create(options.name, options.folder, options.image, options.owner, options.gpgkey_of_owner, options.remote_address)

    elif options.command == start_command_name:
        return core.start(options.configurationfile)

    elif options.command == stop_command_name:
        return core.stop(options.configurationfile)

    elif options.command == apply_configuration_command_name:
        return core.applyconfiguration(options.configurationfile)

    elif options.command == startadvanced_command_name:
        return core.startadvanced(options.configurationfile)

    elif options.command == stopadvanced_command_name:
        return core.stopadvanced(options.configurationfile)

    elif options.command == checkintegrity_command_name:
        return core.checkintegrity(options.configurationfile)

    elif options.command == diagnosis_command_name:
        return core.diagnosis(options.configurationfile)

    else:
        write_message_to_stdout(adame_with_version)
        write_message_to_stdout(f"Run '{product_name} --help' to get help about the usage.")
        return 0

# </miscellaneous>