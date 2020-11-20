import os
import configparser
import socket
import time
import traceback
from argparse import RawTextHelpFormatter
from configparser import ConfigParser
from datetime import datetime
from distutils.spawn import find_executable
import argparse
import psutil
from ScriptCollection.core import ScriptCollection, file_is_empty, folder_is_empty, str_none_safe, ensure_file_exists, write_message_to_stdout, write_message_to_stderr, write_exception_to_stderr_with_traceback, write_text_to_file, ensure_directory_exists, resolve_relative_path_from_current_working_directory, string_has_nonwhitespace_content, current_user_has_elevated_privileges, read_text_from_file, get_time_based_logfile_by_folder, datetime_to_string_for_logfile_entry, string_is_none_or_whitespace

product_name = "Adame"
version = "0.3.0"
__version__ = version
versioned_product_name = f"{product_name} v{version}"


class AdameCore(object):

    # <constants>
    _private_adame_commit_author_name: str = product_name
    _private_configuration_section_general: str = "general"
    _private_configuration_section_general_key_repositoryversion: str = "repositoryversion"
    _private_configuration_section_general_key_formatversion: str = "formatversion"
    _private_configuration_section_general_key_name: str = "name"
    _private_configuration_section_general_key_owner: str = "owner"
    _private_configuration_section_general_key_gpgkeyofowner: str = "gpgkeyofowner"
    _private_configuration_section_general_key_remoteaddress: str = "remoteaddress"
    _private_configuration_section_general_key_remotename: str = "remotename"
    _private_configuration_section_general_key_remotebranch: str = "remotebranch"
    _private_securityconfiguration_section_general: str = "general"
    _private_securityconfiguration_section_general_key_idsname: str = "idsname"
    _private_securityconfiguration_section_general_key_enabledids: str = "enableids"
    _private_securityconfiguration_section_snort: str = "snort"
    _private_securityconfiguration_section_snort_key_globalconfigurationfile: str = "globalconfigurationfile"
    _private_configuration_folder: str = None
    _private_configuration_file: str = None  # Represents "{_private_configuration_folder}/Adame.configuration"
    _private_security_related_configuration_folder: str = None
    _private_repository_folder: str = None
    _private_configuration: ConfigParser = None
    _private_securityconfiguration: ConfigParser = None
    _private_log_folder: str = None  # Represents "{_private_repository_folder}/Logs"
    _private_log_folder_for_internal_overhead: str = None  # Represents "{_private_log_folder}/Overhead"
    _private_log_folder_for_application: str = None  # Represents "{_private_log_folder}/Application"
    _private_log_folder_for_ids: str = None  # Represents "{_private_log_folder}/IDS"
    _private_log_file_for_adame_overhead: str = None

    _private_readme_file: str = None
    _private_license_file: str = None
    _private_gitignore_file: str = None
    _private_dockercompose_file: str = None
    _private_running_information_file: str = None
    _private_applicationprovidedsecurityinformation_file: str = None
    _private_networktrafficgeneratedrules_file: str = None
    _private_networktrafficcustomrules_file: str = None
    _private_logfilepatterns_file: str = None
    _private_propertiesconfiguration_file: str = None

    _private_gpgkey_of_owner_is_available: bool = False
    _private_remote_address_is_available: bool = False

    _private_testrule_trigger_content: str = "adame_testrule_trigger_content_0117ae72-6d1a-4720-8942-610fe9711a01"
    _private_testrule_log_content: str = "adame_testrule_trigger_content_0217ae72-6d1a-4720-8942-610fe9711a02"

    # </constants>

    # <properties>

    verbose: bool = False
    encoding: str = "utf-8"
    format_datetimes_to_utc: bool = True
    check_defer_time_for_checking_that_program_is_running_in_seconds: int = 2

    _private_test_mode: bool = False
    _private_sc: ScriptCollection = ScriptCollection()
    _private_mock_process_queries: list = list()

    # </properties>

    # <initialization>

    def __init__(self):
        self.set_test_mode(False)

    # </initialization>

    # <create-command>

    def create(self, name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str = None, remote_address: str = None) -> int:
        self._private_check_for_elevated_privileges()
        self._private_verbose_log_start_by_create_command(name, folder, image, owner)
        return self._private_execute_task("Create", lambda: self._private_create(name, folder, image, owner, gpgkey_of_owner, remote_address))

    def _private_create(self, name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str, remote_address: str = "") -> None:
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

        self._private_create_adame_configuration_file(configuration_file, name, owner)

        ensure_directory_exists(self._private_security_related_configuration_folder)

        self._private_create_file_in_repository(self._private_readme_file, self._private_get_readme_file_content(self._private_configuration, image))
        self._private_create_file_in_repository(self._private_license_file, self._private_get_license_file_content(self._private_configuration))
        self._private_create_file_in_repository(self._private_gitignore_file, self._private_get_gitignore_file_content())
        self._private_create_file_in_repository(self._private_dockercompose_file, self._private_get_dockercompose_file_content(image))
        self._private_create_file_in_repository(self._private_applicationprovidedsecurityinformation_file, "")
        self._private_create_file_in_repository(self._private_networktrafficgeneratedrules_file, "")
        self._private_create_file_in_repository(self._private_networktrafficcustomrules_file, "")
        self._private_create_file_in_repository(self._private_logfilepatterns_file, self._private_get_logfilepattern_file_content())
        self._private_create_file_in_repository(self._private_propertiesconfiguration_file, "")
        self._private_create_file_in_repository(self._private_running_information_file, self._private_get_running_information_file_content(None, None))

        self._private_create_securityconfiguration_file(gpgkey_of_owner, remote_address)
        self._private_load_securityconfiguration()

        self._private_start_program_synchronously("git", "init", self._private_repository_folder)
        if self._private_gpgkey_of_owner_is_available:
            self._private_start_program_synchronously("git", "config commit.gpgsign true", self._private_repository_folder)
            self._private_start_program_synchronously("git", "config user.signingkey " + gpgkey_of_owner, self._private_repository_folder)

        self._private_commit(f"Initial commit for app-repository of {name} managed by Adame in folder '{self._private_repository_folder}' on host '{socket.gethostname()}'")

    # </create-command>

    # <start-command>

    def start(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        self._private_load_configuration(configurationfile)
        return self._private_execute_task("Start", self._private_start)

    def _private_start(self) -> None:
        if self._private_sc.get_boolean_value_from_configuration(self._private_securityconfiguration, self._private_securityconfiguration_section_general, self._private_securityconfiguration_section_general_key_enabledids):
            process_id_of_ids = self._private_ensure_ids_is_running()
        else:
            process_id_of_ids = None
        process_id_of_container = self._private_ensure_container_is_running()
        self._private_log_running_state(process_id_of_container, process_id_of_ids, "Started")

    # </start-command>

    # <stop-command>

    def stop(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        self._private_load_configuration(configurationfile)
        return self._private_execute_task("Stop", self._private_stop)

    def _private_stop(self) -> None:
        self._private_ensure_container_is_not_running()
        if self._private_sc.get_boolean_value_from_configuration(self._private_securityconfiguration, self._private_securityconfiguration_section_general, self._private_securityconfiguration_section_general_key_enabledids):
            self._private_ensure_ids_is_not_running()
        self._private_log_running_state(None, None, "Stopped")

    # </stop>

    # <applyconfiguration-command>

    def applyconfiguration(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        self._private_load_configuration(configurationfile)
        return self._private_execute_task("ApplyConfiguration", self._private_applyconfiguration)

    def _private_applyconfiguration(self) -> None:
        self._private_check_integrity_of_repository()
        self._private_regenerate_networktrafficgeneratedrules_filecontent()
        self._private_recreate_siem_connection()
        self._private_commit("Reapplied configuration")

    # </applyconfiguration-command>

    # <startadvanced-command>

    def startadvanced(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        self._private_load_configuration(configurationfile)
        return self._private_execute_task("StartAdvanced", self._private_startadvanced)

    def _private_startadvanced(self) -> None:
        self._private_stopadvanced()
        self._private_applyconfiguration()
        self._private_start()

    # </startadvanced-command>

    # <stopadvanced-command>

    def stopadvanced(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        self._private_load_configuration(configurationfile)
        return self._private_execute_task("StopAdvanced", self._private_stopadvanced)

    def _private_stopadvanced(self) -> None:
        self._private_stop()
        self._private_commit("Saved changes")

    # </stopadvanced-command>

    # <checkintegrity-command>

    def checkintegrity(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        self._private_load_configuration(configurationfile)
        return self._private_execute_task("CheckIntegrity", self._private_checkintegrity)

    def _private_checkintegrity(self) -> None:
        self._private_check_integrity_of_repository(7)

    # </checkintegrity-command>

    # <diagnosis-command>

    def diagnosis(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_verbose_log_start_by_configuration_file(configurationfile)
        if configurationfile is not None:
            self._private_load_configuration(configurationfile)
        return self._private_execute_task("Diagnosis", self._private_diagnosis)

    def _private_diagnosis(self) -> None:
        if not self._private_adame_general_diagonisis():
            raise Exception("General diagnosis found discrepancies")
        if self._private_configuration is not None:
            if not self._private_adame_repository_diagonisis():
                raise Exception(f"General diagnosis found discrepancies in repository '{self._private_repository_folder}'")

    # </checkintegrity-command>

    # <other-functions>

    def set_test_mode(self, test_mode_enabled: bool) -> None:
        "This function is for test-purposes only"
        self._private_test_mode = test_mode_enabled
        self._private_sc.mock_program_calls = self._private_test_mode

    def register_mock_process_query(self, process_id: int, command: str) -> None:
        "This function is for test-purposes only"
        r = AdameCore._private_process()
        r.process_id = process_id
        r.command = command
        l = list()
        l.append(r)
        self._private_mock_process_queries.append(l)

    def verify_no_pending_mock_process_queries(self) -> None:
        "This function is for test-purposes only"
        if(len(self._private_mock_process_queries) > 0):
            for mock_query_result in self._private_mock_process_queries:
                raise AssertionError("The following mock-process-query was not queried:\n    "+",\n    ".join([f"'pid: {r.process_id}, command: '{r.command}'" for r in mock_query_result]))

    # </other-functions>

    # <helper-functions>

    def _private_check_for_elevated_privileges(self) -> None:
        if(not current_user_has_elevated_privileges() and not self._private_test_mode):
            raise Exception("Adame requries elevated privileges to get executed")

    def _private_log_running_state(self, process_id_of_container: int, process_id_of_ids: int, action: str) -> None:
        process_id_of_container_as_string = str_none_safe(process_id_of_container)
        process_id_of_ids_as_string = str_none_safe(process_id_of_ids)
        write_text_to_file(self._private_running_information_file, self._private_get_running_information_file_content(process_id_of_container_as_string, process_id_of_ids_as_string))
        self._private_sc.git_unstage_all_changes(self._private_repository_folder)
        self._private_sc.git_stage_file(self._private_repository_folder, self._private_running_information_file)
        self._private_commit(f"{action} container (Container-process: {process_id_of_container_as_string}; IDS-process: {process_id_of_ids_as_string})", False)

    def _private_adame_general_diagonisis(self) -> bool:
        if(not self._private_check_whether_required_tools_for_adame_are_available()):
            return False
        # Add other checks if required
        return True

    def _private_adame_repository_diagonisis(self) -> bool:
        if not self._private_check_whether_required_files_for_adamerepository_are_available():
            return False
        # Add other checks if required
        return True

    def _private_check_whether_required_tools_for_adame_are_available(self) -> bool:
        if self._private_test_mode:
            return True
        else:
            tools = [
                "git",
                "gpg",
                "docker-compose",
            ]
            recommended_tools = [
                "snort",
            ]
            result = True
            for tool in tools:
                if not self._private_tool_exists_in_path(tool):
                    write_message_to_stderr(f"Tool '{tool}' is not available")
            for tool in recommended_tools:
                if not self._private_tool_exists_in_path(tool):
                    self._private_log_warning(f"Recommended tool '{tool}' is not available")
            return result

    def _private_check_whether_required_files_for_adamerepository_are_available(self) -> bool:
        # TODO improve: add checks for files like RunningInformation.txt etc.
        # Add other checks if required
        return True

    def _private_check_configurationfile_argument(self, configurationfile: str) -> None:
        if configurationfile is None:
            raise Exception("Argument 'configurationfile' is not defined")
        if not os.path.isfile(configurationfile):
            raise FileNotFoundError(f"File '{configurationfile}' does not exist")

    def _private_check_integrity_of_repository(self, amount_of_days_of_history_to_check: int = None) -> None:
        """This function checks the integrity of the app-repository.
This function is idempotent."""
        until = datetime.now()
        since = until - datetime.timedelta(days=amount_of_days_of_history_to_check)
        commit_hashs_to_check_in_given_interval = self._private_sc.get_commit_ids_between_dates(self._private_repository_folder, until, since)
        for commithash in commit_hashs_to_check_in_given_interval:
            if not self._private_sc.commit_is_signed_by_key(self._private_repository_folder, commithash, self._private_configuration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_gpgkeyofowner]):
                self._private_log_warning(f"The app-repository '{self._private_repository_folder}' contains the unsigned commit {commithash}", False, True, True)

    def _private_regenerate_networktrafficgeneratedrules_filecontent(self) -> None:
        """This function regenerates the content of the file Networktraffic.Generated.rules.
This function is idempotent."""
        customrules = read_text_from_file(self._private_networktrafficcustomrules_file, self.encoding)
        applicationprovidedrules = "# (not implemented yet)"  # TODO improve: implement usage of application-provided security-information
        file_content = f"""# Rules file for Snort generated by Adame.
# Do not modify this file. Changes will be overwritten.

# Global configuration
include {self._private_securityconfiguration[self._private_securityconfiguration_section_snort][self._private_securityconfiguration_section_snort_key_globalconfigurationfile]}

# Internal rules:
alert tcp any any -> {local_ip_address} any (content: "{self._private_testrule_trigger_content}"; msg: "{self._private_testrule_log_content}"; react: msg;) # Test-rule for functionality test

# Application-provided rules:
{applicationprovidedrules}

# Custom created rules:
{customrules}"""
        write_text_to_file(self._private_networktrafficgeneratedrules_file, file_content, self.encoding)

    def _private_recreate_siem_connection(self) -> None:
        """This function recreate the SIEM-system-connection."""
        # TODO Implement
        # (if required "service rsyslog restart" may be useful)

    def _private_ensure_container_is_running(self) -> int:
        # TODO improve: optimize this function so that the container does not have to be stopped for this function
        self._private_ensure_container_is_not_running()
        return self._private_start_container()

    def _private_ensure_container_is_not_running(self) -> None:
        if(self._private_container_is_running()):
            self._private_stop_container()

    def _private_ensure_ids_is_running(self) -> int:
        """This function ensures that the intrusion-detection-system (ids) is running and the rules will be applied correctly."""
        # TODO improve: optimize this function so that the ids does not have to be stopped for this function
        self._private_ensure_ids_is_not_running()
        process_id = self._private_start_ids()
        self._private_test_ids()
        return process_id

    def _private_ensure_ids_is_not_running(self) -> None:
        """This function ensures that the intrusion-detection-system (ids) is not running anymore."""
        if(self._private_ids_is_running()):
            self._private_stop_ids()

    def _private_ids_is_running(self) -> bool:
        return self._private_is_running_safe(self._private_get_stored_running_processes()[1], self._private_securityconfiguration.get(self._private_securityconfiguration_section_general, self._private_securityconfiguration_section_general_key_idsname))  # TODO improve: add more arguments to command-argument to specify the exptected command better

    def _private_start_ids(self) -> int:
        pid = None
        ids = self._private_securityconfiguration.get(self._private_securityconfiguration_section_general, self._private_securityconfiguration_section_general_key_idsname)
        if(ids == "snort"):
            if self.format_datetimes_to_utc:
                utc_argument = " -U"
            else:
                utc_argument = ""
            if self.verbose:
                verbose_argument = " -v"
            else:
                verbose_argument = ""
            pid = self._private_start_program_asynchronously("snort", f'-i {networkinterface} -c "{self._private_networktrafficgeneratedrules_file}" -l "{self._private_log_folder_for_ids}"{utc_argument}{verbose_argument} -x -y -K ascii', "")
        return pid

    def _private_stop_ids(self) -> None:
        ids = self._private_securityconfiguration.get(self._private_securityconfiguration_section_general, self._private_securityconfiguration_section_general_key_idsname)
        if(ids == "snort"):
            self._private_start_program_synchronously("kill", f"-9 {self._private_get_stored_running_processes()[1]}")
            for process in self._private_get_running_processes():
                if("snort" in process.command and self._private_repository_folder in process.command):
                    self._private_start_program_synchronously("kill", f"-9 {process.process_id}")

    def _private_test_ids(self):
        pass  # TODO improve: test if a specific test-rule will be applied by sending a package to the docker-container which should be result in a log-folder

    def _private_get_stored_running_processes(self) -> tuple:
        lines = read_text_from_file(self._private_running_information_file).splitlines()
        processid_of_container_as_string = None
        processid_of_ids_as_string = None
        for line in lines:
            if ":" in line:
                splitted = line.split(":")
                value_as_string = splitted[1].strip()
                if string_has_nonwhitespace_content(value_as_string):
                    value = int(value_as_string)
                    if splitted[0] == "Container-process":
                        processid_of_container_as_string = value
                    if splitted[0] == "IDS-process":
                        processid_of_ids_as_string = value
        return (processid_of_container_as_string, processid_of_ids_as_string)

    def _private_get_running_information_file_content(self, processid_of_container: int, processid_of_network_ids: int) -> str:
        processid_of_container_as_string = str_none_safe(processid_of_container)
        processid_of_ids_as_string = str_none_safe(processid_of_network_ids)
        return f"""Container-process:{processid_of_container_as_string}
IDS-process:{processid_of_ids_as_string}
"""

    def _private_get_logfilepattern_file_content(self):
        return f"""{self._private_log_folder}/**
"""

    def _private_create_adame_configuration_file(self, configuration_file: str, name: str, owner: str) -> None:
        self._private_configuration_file = configuration_file
        ensure_directory_exists(os.path.dirname(self._private_configuration_file))
        local_configparser = ConfigParser()

        local_configparser.add_section(self._private_configuration_section_general)
        local_configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_formatversion] = version
        local_configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_repositoryversion] = "1.0.0"
        local_configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_name] = name
        local_configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_owner] = owner

        with open(self._private_configuration_file, 'w+', encoding=self.encoding) as configfile:
            local_configparser.write(configfile)
        self._private_log_information(f"Created file '{self._private_configuration_file}'", True)

        self._private_load_configuration(self._private_configuration_file, False)

    def _private_verbose_log_start_by_configuration_file(self, configurationfile: str) -> None:
        self._private_log_information(f"Started Adame with configurationfile '{configurationfile}'", True)

    def _private_verbose_log_start_by_create_command(self, name: str, folder: str, image: str, owner: str) -> None:
        self._private_log_information(f"Started Adame with  name='{str_none_safe(name)}', folder='{str_none_safe(folder)}', image='{str_none_safe(image)}', owner='{str_none_safe(owner)}'", True)

    def _private_load_configuration(self, configurationfile: str, load_securityconfiguration: bool = True) -> None:
        try:
            configurationfile = resolve_relative_path_from_current_working_directory(configurationfile)
            if not os.path.isfile(configurationfile):
                raise Exception(F"'{configurationfile}' does not exist")
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
            self._private_running_information_file = os.path.join(self._private_configuration_folder, "RunningInformation.txt")
            self._private_dockercompose_file = os.path.join(self._private_configuration_folder, "docker-compose.yml")
            self._private_applicationprovidedsecurityinformation_file = os.path.join(self._private_security_related_configuration_folder, "ApplicationProvidedSecurityInformation.xml")
            self._private_networktrafficgeneratedrules_file = os.path.join(self._private_security_related_configuration_folder, "Networktraffic.Generated.rules")
            self._private_networktrafficcustomrules_file = os.path.join(self._private_security_related_configuration_folder, "Networktraffic.Custom.rules")
            self._private_logfilepatterns_file = os.path.join(self._private_security_related_configuration_folder, "LogfilePatterns.txt")
            self._private_propertiesconfiguration_file = os.path.join(self._private_security_related_configuration_folder, "Security.configuration")

            self._private_log_folder = os.path.join(self._private_repository_folder, "Logs")
            self._private_log_folder_for_application = os.path.join(self._private_log_folder, "Application")
            ensure_directory_exists(self._private_log_folder_for_application)
            self._private_log_folder_for_ids = os.path.join(self._private_log_folder, "IDS")
            ensure_directory_exists(self._private_log_folder_for_ids)
            self._private_log_folder_for_internal_overhead = os.path.join(self._private_log_folder, "Overhead")
            ensure_directory_exists(self._private_log_folder_for_internal_overhead)
            self._private_log_file_for_adame_overhead = get_time_based_logfile_by_folder(self._private_log_folder_for_internal_overhead, product_name, self.format_datetimes_to_utc)
            ensure_file_exists(self._private_log_file_for_adame_overhead)

            if load_securityconfiguration:
                self._private_load_securityconfiguration()

        except Exception as exception:
            self._private_log_exception(f"Error while loading configurationfile '{configurationfile}'.", exception)
            raise

    def _private_load_securityconfiguration(self) -> None:
        try:
            securityconfiguration = configparser.ConfigParser()
            if not os.path.isfile(self._private_propertiesconfiguration_file):
                raise Exception(F"'{self._private_propertiesconfiguration_file}' does not exist")
            securityconfiguration.read(self._private_propertiesconfiguration_file)
            self._private_securityconfiguration = securityconfiguration

            self._private_gpgkey_of_owner_is_available = string_has_nonwhitespace_content(self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_gpgkeyofowner])
            self._private_remote_address_is_available = string_has_nonwhitespace_content(self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remoteaddress])

            if(not self._private_gpgkey_of_owner_is_available):
                self._private_log_information("Warning: GPGKey of the owner of the repository is not set. It is highly recommended to set this value to ensure the integrity of the app-repository.")
            if(not self._private_remote_address_is_available):
                self._private_log_information("Warning: Remote-address of the repository is not set. It is highly recommended to set this value to save the content of the app-repository externally.")

        except Exception as exception:
            self._private_log_exception(f"Error while loading configurationfile '{self._private_propertiesconfiguration_file}'.", exception)
            raise

    def _private_get_container_name(self) -> str:
        return self._private_name_to_docker_allowed_name(self._private_configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_name))

    def _private_get_dockercompose_file_content(self, image: str) -> str:
        name_as_docker_allowed_name = self._private_get_container_name()
        return f"""version: '3.2'
services:
  {name_as_docker_allowed_name}:
    image: '{image}'
    container_name: '{name_as_docker_allowed_name}'
#     environment:
#       - variable=value
#     ports:
#       - 443:443
#     volumes:
#       - ./Volumes/Configuration:/DirectoryInContainer/Configuration
#       - ./Volumes/Data:/DirectoryInContainer/Data
#       - ./../Logs/Application:/DirectoryInContainer/Logs
"""

    def _private_create_file_in_repository(self, file, filecontent) -> None:
        write_text_to_file(file, filecontent, self.encoding)
        self._private_log_information(f"Created file '{file}'", True)

    def _private_get_license_file_content(self, configuration: ConfigParser) -> str:
        return f"""Owner of this repository and its content: {configuration.get(self._private_configuration_section_general, self._private_configuration_section_general_key_owner)}
Only the owner of this repository is allowed to read, use, change, publish this repository or its content.
Only the owner of this repository is allowed to change the license of this repository or its content.
"""

    def _private_get_gitignore_file_content(self) -> str:
        return """Logs/**
"""

    def _private_create_securityconfiguration_file(self, gpgkey_of_owner: str, remote_address: str):
        securityconfiguration = ConfigParser()
        securityconfiguration.add_section(self._private_securityconfiguration_section_general)
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_enabledids] = "false"
        self._private_add_default_ids_configuration_to_securityconfiguration(securityconfiguration, gpgkey_of_owner, remote_address)

        with open(self._private_propertiesconfiguration_file, 'w+', encoding=self.encoding) as configfile:
            securityconfiguration.write(configfile)

    def _private_add_default_ids_configuration_to_securityconfiguration(self, securityconfiguration: ConfigParser, gpgkey_of_owner: str, remote_address: str) -> None:

        securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_gpgkeyofowner] = gpgkey_of_owner
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remoteaddress] = remote_address
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remotename] = "Backup"
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remotebranch] = "master"
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_enabledids] = "true"
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_idsname] = "snort"
        securityconfiguration.add_section(self._private_securityconfiguration_section_snort)
        securityconfiguration[self._private_securityconfiguration_section_snort][self._private_securityconfiguration_section_snort_key_globalconfigurationfile] = "/etc/snort/snort.conf"

    def _private_get_readme_file_content(self, configuration: ConfigParser, image: str) -> str:

        if self._private_remote_address_is_available:
            remote_address_info = f"The data of this repository will be saved as backup in '{configuration.get(self._private_securityconfiguration_section_general, self._private_configuration_section_general_key_remoteaddress)}'."
        else:
            remote_address_info = "Currently there is no backup-address defined for backups of this repository."

        if self._private_gpgkey_of_owner_is_available:
            gpgkey_of_owner_info = f"The integrity of the data of this repository will ensured using the GPG-key {configuration.get(self._private_securityconfiguration_section_general, self._private_configuration_section_general_key_gpgkeyofowner)}."
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

    def _private_stop_container(self) -> None:
        self._private_start_program_synchronously("docker-compose", "down --remove-orphans", self._private_configuration_folder)
        self._private_log_information("Container was stopped", False, True, True)

    def _private_start_container(self) -> int:
        process_id = self._private_start_program_asynchronously("docker-compose", "up --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps", self._private_configuration_folder)
        self._private_log_information("Container was started", False, True, True)
        return process_id

    def _private_container_is_running(self) -> bool:
        return self._private_get_stored_running_processes()[0] is not None

    def _private_is_running_safe(self, index: int, command: str) -> bool:
        if(index is None):
            return False
        else:
            return self._private_process_is_running(index, command)

    def _private_get_running_processes(self) -> list:
        if self._private_test_mode:
            if len(self._private_mock_process_queries) == 0:
                raise LookupError("Tried to query process-list but no mock-queries are available anymore")
            else:
                return self._private_mock_process_queries.pop(0)
        else:
            result = list()
            for item in psutil.process_iter():
                try:
                    process = AdameCore._private_process()
                    process.process_id = item.pid
                    process.command = " ".join(item.cmdline())
                    result.append(process)
                except psutil.AccessDenied:
                    pass  # The process searched for is always queryable. Some other processes may not be queryable but they can be ignored since they are not relevant for this use-case.
            return result

    def _private_process_is_running(self, process_id: int, command: str) -> bool:
        for process in self._private_get_running_processes():
            if(self._private_process_is_running_helper(process.process_id, process.command, process_id, command)):
                return True
        return False

    def _private_process_is_running_helper(self, actual_pid: int, actual_command: str, expected_pid: int, expected_command: str) -> bool:
        if actual_pid == expected_pid:
            if expected_command in actual_command:
                return True
            else:
                if(string_is_none_or_whitespace(actual_command)):
                    self._private_log_warning(f"It seems that the process with id {expected_pid} was not executed", False, True, False)
                else:
                    self._private_log_warning(f"The process with id {expected_pid} changed unexpectedly. Expected a process with a commandline like '{expected_command}...' but was '{actual_command}...'", False, True, False)
        return False

    def _private_commit(self, message: str, stage_all_changes: bool = True) -> None:
        repository = self._private_repository_folder
        commit_id = self._private_sc.git_commit(repository, message, self._private_adame_commit_author_name, "", stage_all_changes)
        remote_name = self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remotename]
        branch_name = self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remotebranch]
        remote_address = self._private_securityconfiguration.get(self._private_securityconfiguration_section_general, self._private_configuration_section_general_key_remoteaddress)
        self._private_log_information(f"Created commit {commit_id} ('{message}') in repository '{repository}'", False, True, True)
        if self._private_remote_address_is_available:
            self._private_sc.git_add_or_set_remote_address(self._private_repository_folder, remote_name, remote_address)
            self._private_sc.git_push(self._private_repository_folder, remote_name, branch_name, branch_name, False, False)
            self._private_log_information(f"Pushed repository '{repository}' to remote {remote_address}", False, True, True)
        else:
            self._private_log_warning("Either no remote-address is defined or the remote-address for the backup of the app-repository is not available.")

    def _private_name_to_docker_allowed_name(self, name: str) -> str:
        name = name.lower()
        return name

    def _private_start_program_asynchronously(self, program: str, argument: str, workingdirectory: str = None) -> int:
        self._private_log_information(f"Start program '{workingdirectory}>{program} {argument}'", True)
        pid = self._private_sc.start_program_asynchronously(program, argument, workingdirectory)
        time.sleep(self.check_defer_time_for_checking_that_program_is_running_in_seconds)
        if not self._private_process_is_running(pid, program):
            raise Exception(f"Process '{workingdirectory}>{program} {argument}' (process-id {pid}) exited unexpectedly")
        self._private_log_information(f"Started program has processid {pid}", True)
        return pid

    def _private_start_program_synchronously(self, program: str, argument: str, workingdirectory: str = None, expect_exitcode_zero: bool = True) -> list:
        workingdirectory = str_none_safe(workingdirectory)
        self._private_log_information(f"Start program '{workingdirectory}>{program} {argument}'", True)
        if self.verbose:
            verbose_argument = 2
        else:
            verbose_argument = 1
        result = self._private_sc.start_program_synchronously(program, argument, workingdirectory, verbose_argument, False, None, 3600, False, None, expect_exitcode_zero, True, False)
        self._private_log_information(f"Program resulted in exitcode {result[0]}", True)
        self._private_log_information("Stdout:", True)
        self._private_log_information(result[1], True)
        self._private_log_information("Stderr:", True)
        self._private_log_information(result[2], True)
        return result

    def _private_tool_exists_in_path(self, name: str) -> bool:
        return find_executable(name) is not None

    class _private_process:
        "This class is for test-purposes only"
        process_id: str
        command: str

    def _private_execute_task(self, name: str, function) -> int:
        exitcode = 0
        try:
            self._private_log_information(f"Started task '{name}'")
            function()
        except Exception as exception:
            exitcode = 1
            self._private_log_exception(f"Exception occurred in task '{name}'", exception)
        finally:
            self._private_log_information(f"Finished task '{name}'. Task resulted in exitcode {exitcode}")
        return exitcode

    def _private_log_information(self, message: str, is_verbose_log_entry: bool = False, write_to_console: bool = True, write_to_logfile: bool = False) -> None:
        self._private_write_to_log("Information", message, is_verbose_log_entry, write_to_console, write_to_logfile)

    def _private_log_warning(self, message: str, is_verbose_log_entry: bool = False, write_to_console: bool = True, write_to_logfile: bool = False) -> None:
        self._private_write_to_log("Warning", message, is_verbose_log_entry, write_to_console, write_to_logfile)

    def _private_log_error(self, message: str, is_verbose_log_entry: bool = False, write_to_console: bool = True, write_to_logfile: bool = False) -> None:
        self._private_write_to_log("Error", message, is_verbose_log_entry, write_to_console, write_to_logfile)

    def _private_log_exception(self, message: str, exception: Exception, is_verbose_log_entry: bool = False, write_to_console: bool = True, write_to_logfile: bool = True) -> None:
        self._private_write_to_log("Error", f"{message}; {str(exception)}", is_verbose_log_entry, write_to_console, write_to_logfile)
        if(self.verbose):
            write_exception_to_stderr_with_traceback(exception, traceback, message)

    def _private_write_to_log(self, loglevel: str, message: str, is_verbose_log_entry: bool, write_to_console: bool, write_to_logfile: bool) -> None:
        if is_verbose_log_entry and not self.verbose:
            return
        if(self.format_datetimes_to_utc):
            date_as_string = datetime.utcnow()
        else:
            date_as_string = datetime.now()
        logentry = f"[{datetime_to_string_for_logfile_entry(date_as_string)}] [{loglevel}] {message}"
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


def get_adame_version() -> str:
    return version


def adame_cli() -> int:
    arger = argparse.ArgumentParser(description=f"""{versioned_product_name}
Adame (Automatic Docker Application Management Engine) is a tool which manages (install, start, stop) docker-applications.
One focus of Adame is to store the state of an application: Adame stores all data of the application in a git-repository. So with Adame it is very easy move the application with all its data and configurations to another computer.
Another focus of Adame is IT-forensics and IT-security: Adame generates a basic ids-configuration for each application to detect/log/block networktraffic from the docker-container of the application which is obvious harmful.

Required commandline-commands:
-docker-compose
-git
-sudo

Recommended commandline-commands:
-gpg
-snort

Adame must be executed with elevated privileges. This is required to run commands like docker-compose or snort.
""", formatter_class=RawTextHelpFormatter)

    arger.add_argument("-v", "--verbose", action="store_true", required=False, default=False)

    subparsers = arger.add_subparsers(dest="command")

    create_command_name = "create"
    create_parser = subparsers.add_parser(create_command_name)
    create_parser.add_argument("-n", "--name", required=True)
    create_parser.add_argument("-f", "--folder", required=True)
    create_parser.add_argument("-i", "--image", required=True)
    create_parser.add_argument("-o", "--owner", required=True)
    create_parser.add_argument("-g", "--gpgkey_of_owner", required=False)
    create_parser.add_argument("-r", "--remote_address", required=False)

    start_command_name = "start"
    start_parser = subparsers.add_parser(start_command_name)
    start_parser.add_argument("-c", "--configurationfile", required=True)

    stop_command_name = "stop"
    stop_parser = subparsers.add_parser(stop_command_name)
    stop_parser.add_argument("-c", "--configurationfile", required=True)

    apply_configuration_command_name = "applyconfiguration"
    apply_configuration_parser = subparsers.add_parser(apply_configuration_command_name)
    apply_configuration_parser.add_argument("-c", "--configurationfile", required=True)

    startadvanced_command_name = "startadvanced"
    startadvanced_parser = subparsers.add_parser(startadvanced_command_name)
    startadvanced_parser.add_argument("-c", "--configurationfile", required=True)

    stopadvanced_command_name = "stopadvanced"
    stopadvanced_parser = subparsers.add_parser(stopadvanced_command_name)
    stopadvanced_parser.add_argument("-c", "--configurationfile", required=True)

    checkintegrity_command_name = "checkintegrity"
    checkintegrity_parser = subparsers.add_parser(checkintegrity_command_name)
    checkintegrity_parser.add_argument("-c", "--configurationfile", required=True)

    diagnosis_command_name = "diagnosis"
    diagnosis_parser = subparsers.add_parser(diagnosis_command_name)
    diagnosis_parser.add_argument("-c", "--configurationfile", required=False)

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
        write_message_to_stdout(versioned_product_name)
        write_message_to_stdout(f"Run '{product_name} --help' to get help about the usage.")
        return 0

# </miscellaneous>


if __name__ == '__main__':
    adame_cli()
