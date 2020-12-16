import os
import configparser
import socket
import traceback
import uuid
from argparse import RawTextHelpFormatter
from configparser import ConfigParser
from datetime import datetime, timedelta
from distutils.spawn import find_executable
import argparse
import psutil
from ScriptCollection.core import ScriptCollection, file_is_empty, folder_is_empty, str_none_safe, ensure_file_exists, write_message_to_stdout, write_message_to_stderr, write_exception_to_stderr_with_traceback, write_text_to_file, ensure_directory_exists, resolve_relative_path_from_current_working_directory, string_has_nonwhitespace_content, current_user_has_elevated_privileges, read_text_from_file, get_time_based_logfile_by_folder, datetime_to_string_for_logfile_entry, string_is_none_or_whitespace, string_to_boolean, get_direct_files_of_folder, get_time_based_logfilename
import netifaces

product_name = "Adame"
version = "0.6.1"
__version__ = version
versioned_product_name = f"{product_name} v{version}"


class AdameCore(object):

    # <constants>
    _private_adame_commit_author_name: str = product_name
    _private_configuration_section_general: str = "general"
    _private_configuration_section_general_key_networkinterface: str = "networkinterface"
    _private_configuration_section_general_key_repositoryid: str = "repositoryid"
    _private_configuration_section_general_key_repositoryversion: str = "repositoryversion"
    _private_configuration_section_general_key_formatversion: str = "formatversion"
    _private_configuration_section_general_key_name: str = "name"
    _private_configuration_section_general_key_owner: str = "owner"
    _private_configuration_section_general_key_gpgkeyofowner: str = "gpgkeyofowner"
    _private_configuration_section_general_key_remoteaddress: str = "remoteaddress"
    _private_configuration_section_general_key_remotename: str = "remotename"
    _private_configuration_section_general_key_remotebranch: str = "remotebranch"
    _private_securityconfiguration_section_general: str = "general"
    _private_securityconfiguration_section_general_key_siemaddress: str = "siemaddress"
    _private_securityconfiguration_section_general_key_siemfolder: str = "siemfolder"
    _private_securityconfiguration_section_general_key_siemuser: str = "siemuser"
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
    _private_propertiesconfiguration_file: str = None

    _private_gpgkey_of_owner_is_available: bool = False
    _private_remote_address_is_available: bool = False

    _private_testrule_trigger_content: str = "adame_testrule_trigger_content_0117ae72-6d1a-4720-8942-610fe9711a01"
    _private_testrule_log_content: str = "adame_testrule_trigger_content_0217ae72-6d1a-4720-8942-610fe9711a02"
    _private_testrule_sid: str = "8979665"
    _private_localipaddress_placeholder: str = "__localipaddress__"

    # </constants>

    # <properties>

    verbose: bool = False
    encoding: str = "utf-8"
    format_datetimes_to_utc: bool = True

    _private_test_mode: bool = False
    _private_sc: ScriptCollection = ScriptCollection()
    _private_mock_process_queries: list = list()

    # </properties>

    # <initialization>

    def __init__(self):
        self.set_test_mode(False)

    # </initialization>

    # <create-command>

    def create(self, name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str = None) -> int:
        self._private_check_for_elevated_privileges()
        self._private_verbose_log_start_by_create_command(name, folder, image, owner)
        return self._private_execute_task("Create", lambda: self._private_create(name, folder, image, owner, gpgkey_of_owner))

    def _private_create(self, name: str, folder: str, image: str, owner: str, gpgkey_of_owner: str) -> None:
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
        self._private_create_file_in_repository(self._private_propertiesconfiguration_file, "")
        self._private_create_file_in_repository(self._private_running_information_file, self._private_get_running_information_file_content(False, False))

        self._private_create_securityconfiguration_file(gpgkey_of_owner)
        self._private_load_securityconfiguration()

        self._private_start_program_synchronously("chmod", f'-R 777 "{self._private_log_folder_for_ids}"')  # TODO Improve: Shrink 777 as far as possible

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
            ids_is_running = self._private_ensure_ids_is_running()
        else:
            ids_is_running = False
        container_is_running = self._private_ensure_container_is_running()
        self._private_log_running_state(container_is_running, ids_is_running, "Started")

    # </start-command>

    # <stop-command>

    def stop(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        self._private_load_configuration(configurationfile)
        return self._private_execute_task("Stop", self._private_stop)

    def _private_stop(self) -> None:
        container_is_running = not self._private_ensure_container_is_not_running()
        ids_is_running = False
        if self._private_sc.get_boolean_value_from_configuration(self._private_securityconfiguration, self._private_securityconfiguration_section_general, self._private_securityconfiguration_section_general_key_enabledids):
            ids_is_running = not self._private_ensure_ids_is_not_running()
        self._private_log_running_state(container_is_running, ids_is_running, "Stopped")

    # </stop>

    # <applyconfiguration-command>

    def applyconfiguration(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        self._private_load_configuration(configurationfile)
        return self._private_execute_task("ApplyConfiguration", self._private_applyconfiguration)

    def _private_applyconfiguration(self) -> None:
        self._private_regenerate_networktrafficgeneratedrules_filecontent()
        if not self._private_check_siem_is_reachable():
            self._private_log_warning("The SIEM-connection is missing", False, True, True)
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
        self._private_exportlogs()

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

    # <exportlogs-command>

    def exportlogs(self, configurationfile: str) -> int:
        self._private_check_for_elevated_privileges()
        self._private_check_configurationfile_argument(configurationfile)

        self._private_verbose_log_start_by_configuration_file(configurationfile)
        self._private_load_configuration(configurationfile)
        return self._private_execute_task("ExportLogs", self._private_exportlogs)

    def _private_exportlogs(self) -> None:
        if(not self._private_tool_exists_in_path("rsync")):
            self._private_log_warning("rsync is not available", False, True, True)
            return

        if(not self._private_check_siem_is_reachable()):
            self._private_log_warning("The log-files can not be exported due to a missing SIEM-connection", False, True, True)
            return

        siemaddress = self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_siemaddress]
        siemfolder = self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_siemfolder]
        siemuser = self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_siemuser]
        log_files = get_direct_files_of_folder(self._private_log_folder_for_internal_overhead)+get_direct_files_of_folder(self._private_log_folder_for_ids)+get_direct_files_of_folder(self._private_log_folder_for_application)
        sublogfolder = get_time_based_logfilename("Log", self.format_datetimes_to_utc)
        for log_file in log_files:
            exitcode = self._private_start_program_synchronously("rsync", f'--compress --verbose --rsync-path="mkdir -p {siemfolder}/{sublogfolder}/ && rsync" -e ssh {log_file} {siemuser}@{siemaddress}:{siemfolder}/{sublogfolder}', "", False)[0]
            if(exitcode == 0):
                self._private_log_information(f"Logfile '{log_file}' was successfully exported to {siemaddress}", True, True, True)
                os.remove(log_file)
            else:
                self._private_log_warning(f"Exporting Log-file '{log_file}' to {siemaddress} resulted in exitcode {str(exitcode)}", False, True, True)

    # </exportlogs-command>

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
        process = AdameCore._private_process()
        process.process_id = process_id
        process.command = command
        resultlist = list()
        resultlist.append(process)
        self._private_mock_process_queries.append(resultlist)

    def verify_no_pending_mock_process_queries(self) -> None:
        "This function is for test-purposes only"
        if(len(self._private_mock_process_queries) > 0):
            for mock_query_result in self._private_mock_process_queries:
                raise AssertionError("The following mock-process-queries were not queried:\n    "+",\n    ".join([f"'pid: {r.process_id}, command: '{r.command}'" for r in mock_query_result]))

    # </other-functions>

    # <helper-functions>

    def _private_check_for_elevated_privileges(self) -> None:
        if(not current_user_has_elevated_privileges() and not self._private_test_mode):
            raise Exception("Adame requries elevated privileges to get executed")

    def _private_log_running_state(self, container_is_running: bool, ids_is_running: bool, action: str) -> None:
        write_text_to_file(self._private_running_information_file, self._private_get_running_information_file_content(container_is_running, ids_is_running))
        self._private_sc.git_unstage_all_changes(self._private_repository_folder)
        self._private_sc.git_stage_file(self._private_repository_folder, self._private_running_information_file)
        self._private_commit(f"{action} container (Container-process: {str(container_is_running)}; IDS-process: {str(ids_is_running)})", False)

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
        result = True
        if not self._private_test_mode:
            return result
        tools = [
            "chmod",
            "docker-compose",
            "git",
        ]
        recommended_tools = [
            "gpg",
            "rsync",
            "ssh",
            "snort",
        ]
        for tool in tools:
            if not self._private_tool_exists_in_path(tool):
                write_message_to_stderr(f"Tool '{tool}' is not available")
                result = False
        for tool in recommended_tools:
            if not self._private_tool_exists_in_path(tool):
                self._private_log_warning(f"Recommended tool '{tool}' is not available")
                result = False
        return result

    def _private_check_whether_required_files_for_adamerepository_are_available(self) -> bool:
        # TODO Improve: Add checks for files like RunningInformation.txt etc.
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
        since = until - timedelta(days=amount_of_days_of_history_to_check)
        commit_hashs_to_check_in_given_interval = self._private_sc.get_commit_ids_between_dates(self._private_repository_folder, until, since)
        for commithash in commit_hashs_to_check_in_given_interval:
            if not self._private_sc.commit_is_signed_by_key(self._private_repository_folder, commithash, self._private_configuration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_gpgkeyofowner]):
                self._private_log_warning(f"The app-repository '{self._private_repository_folder}' contains the unsigned commit {commithash}", False, True, True)

    def get_entire_testrule_trigger_content(self) -> str:
        return f"testrule_content_{self._private_testrule_trigger_content}_{self._private_configuration[self._private_configuration_section_general][self._private_configuration_section_general_key_repositoryid]}"

    def get_entire_testrule_trigger_answer(self) -> str:
        return f"testrule_answer_{self._private_testrule_log_content}_{self._private_configuration[self._private_configuration_section_general][self._private_configuration_section_general_key_repositoryid]}"

    def _private_regenerate_networktrafficgeneratedrules_filecontent(self) -> None:
        """This function regenerates the content of the file Networktraffic.Generated.rules.
This function is idempotent."""
        customrules = read_text_from_file(self._private_networktrafficcustomrules_file, self.encoding)
        applicationprovidedrules = "# (not implemented yet)"  # TODO Improve: Implement usage of application-provided security-information
        local_ip_address = self._private_get_local_ip_address()
        file_content = f"""# Rules file for Snort generated by Adame.
# Do not modify this file. Changes will be overwritten.

# --- Global configuration ---
# TODO include {self._private_securityconfiguration[self._private_securityconfiguration_section_snort][self._private_securityconfiguration_section_snort_key_globalconfigurationfile]}

# --- Internal rules ---

# Test-rule for functionality test:
# TODO alert tcp any any -> {self._private_localipaddress_placeholder} any (sid: {self._private_testrule_sid}; content: "{self.get_entire_testrule_trigger_content()}"; msg: "{self.get_entire_testrule_trigger_answer()}";)

# --- Application-provided rules ---
{applicationprovidedrules}

# --- Custom created rules ---
{customrules}
"""
        file_content = file_content.replace(self._private_localipaddress_placeholder, local_ip_address)  # replacement to allow to use this variable in the customrules.
        write_text_to_file(self._private_networktrafficgeneratedrules_file, file_content, self.encoding)

    def _private_check_siem_is_reachable(self) -> bool:
        """This function checks wether the SIEM is available."""
        # siemaddress=self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_siemaddress]
        return True  # TODO Improve: Return true if and only if siemaddress is available to receive log-files

    def _private_ensure_container_is_running(self) -> bool:
        # TODO Improve: Optimize this function so that the container does not have to be stopped for this function
        self._private_ensure_container_is_not_running()
        result = self._private_start_container()
        return result

    def _private_ensure_container_is_not_running(self) -> bool:
        if(self._private_container_is_running()):
            return self._private_stop_container()
        return True

    def _private_ensure_ids_is_running(self) -> bool:
        """This function ensures that the intrusion-detection-system (ids) is running and the rules will be applied correctly."""
        # TODO Improve: Optimize this function so that the ids does not have to be stopped for this function
        self._private_ensure_ids_is_not_running()
        result = self._private_start_ids()
        self._private_test_ids()
        return result

    def _private_ensure_ids_is_not_running(self) -> bool:
        """This function ensures that the intrusion-detection-system (ids) is not running anymore."""
        if(self._private_ids_is_running()):
            return self._private_stop_ids()
        return True

    def _private_container_is_running(self) -> bool:
        return self._private_get_stored_running_processes()[0]

    def _private_ids_is_running(self) -> bool:
        ids = self._private_securityconfiguration.get(self._private_securityconfiguration_section_general, self._private_securityconfiguration_section_general_key_idsname)
        if(ids == "snort"):
            return self._private_get_stored_running_processes()[1]

    def _private_start_ids(self) -> bool:
        success = True
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
            networkinterface = self._private_configuration[self._private_configuration_section_general][self._private_configuration_section_general_key_networkinterface]
            success = self._private_run_system_command("snort", f'-D -i {networkinterface} -c "{self._private_networktrafficgeneratedrules_file}" -l "{self._private_log_folder_for_ids}"{utc_argument}{verbose_argument} -x -y -K ascii')
        if success:
            self._private_log_information("IDS was started", False, True, True)
        else:
            self._private_log_warning("IDS could not be started")
        return success

    def _private_stop_ids(self) -> bool:
        result = 0
        ids = self._private_securityconfiguration.get(self._private_securityconfiguration_section_general, self._private_securityconfiguration_section_general_key_idsname)
        if(ids == "snort"):
            for process in self._private_get_running_processes():
                if(process.command.startswith("snort") and self._private_repository_folder in process.command):
                    result = self._private_start_program_synchronously("kill", f"-TERM {process.process_id}")[0]
                    if result != 0:
                        result = self._private_start_program_synchronously("kill", f"-9 {process.process_id}")[0]
        result = 0
        success = result == 0
        if success:
            self._private_log_information("IDS was stopped", False, True, True)
        else:
            self._private_log_warning("IDS could not be stopped")
        return success

    def _private_test_ids(self) -> None:
        pass  # TODO Improve: Test if a specific test-rule will be applied by sending a package to the docker-container which should be result in a log-folder

    def _private_run_system_command(self, program: str, argument: str, working_directory: str = None) -> bool:
        """Starts a program which should be organize its asynchronous execution by itself. This function ensures that the asynchronous program will not get terminated when Adame terminates."""
        if(working_directory is None):
            working_directory = os.getcwd()
        working_directory = resolve_relative_path_from_current_working_directory(working_directory)
        self._private_log_information(f"Start '{working_directory}>{program} {argument}'", True, True, True)
        if self._private_test_mode:
            self._private_start_program_synchronously(program, argument, working_directory)  # mocks defined in self._private_sc will be used here when running the unit-tests
        else:
            original_cwd = os.getcwd()
            if(string_is_none_or_whitespace(working_directory)):
                working_directory = original_cwd
            os.chdir(working_directory)
            try:
                os.system(f"{program} {argument}")
            finally:
                os.chdir(original_cwd)
        return True  # TODO Improve: Find a possibility to really check that this program is running now

    def _private_get_stored_running_processes(self) -> tuple:
        # TODO Improve: Do a real check, not just reading this information from a file.
        lines = read_text_from_file(self._private_running_information_file).splitlines()
        processid_of_container_as_string = False
        processid_of_ids_as_string = False
        for line in lines:
            if ":" in line:
                splitted = line.split(":")
                value_as_string = splitted[1].strip()
                if string_has_nonwhitespace_content(value_as_string):
                    value = string_to_boolean(value_as_string)
                    if splitted[0] == "Container-process":
                        processid_of_container_as_string = value
                    if splitted[0] == "IDS-process":
                        processid_of_ids_as_string = value
        return (processid_of_container_as_string, processid_of_ids_as_string)

    def _private_get_running_information_file_content(self, container_is_running: bool, ids_is_running: int) -> str:
        container_is_running_as_string = str(container_is_running)
        ids_is_running_as_string = str(ids_is_running)
        return f"""Container-process:{container_is_running_as_string}
IDS-process:{ids_is_running_as_string}
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
        local_configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_repositoryid] = str(uuid.uuid4())
        local_configparser[self._private_configuration_section_general][self._private_configuration_section_general_key_networkinterface] = "eth0"

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

    def _private_create_securityconfiguration_file(self, gpgkey_of_owner: string_to_boolean) -> None:
        securityconfiguration = ConfigParser()
        securityconfiguration.add_section(self._private_securityconfiguration_section_general)
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_enabledids] = "false"
        self._private_add_default_ids_configuration_to_securityconfiguration(securityconfiguration, gpgkey_of_owner)

        with open(self._private_propertiesconfiguration_file, 'w+', encoding=self.encoding) as configfile:
            securityconfiguration.write(configfile)

    def _private_add_default_ids_configuration_to_securityconfiguration(self, securityconfiguration: ConfigParser, gpgkey_of_owner: str) -> None:

        securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_gpgkeyofowner] = gpgkey_of_owner
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remoteaddress] = ""
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remotename] = "Backup"
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remotebranch] = "master"
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_enabledids] = "true"
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_idsname] = "snort"
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_siemaddress] = ""
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_siemfolder] = f"/var/log/{socket.gethostname()}/{self._private_get_container_name()}"
        securityconfiguration[self._private_securityconfiguration_section_general][self._private_securityconfiguration_section_general_key_siemuser] = "username_on_siem_system"
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
        result = self._private_start_program_synchronously("docker-compose", "down --remove-orphans", self._private_configuration_folder)[0]
        success = result == 0
        if success:
            self._private_log_information("Container was stopped", False, True, True)
        else:
            self._private_log_warning("Container could not be stopped")
        return success

    def _private_start_container(self) -> bool:
        success = self._private_run_system_command("docker-compose", "up --detach --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps", self._private_configuration_folder)
        if success:
            self._private_log_information("Container was started", False, True, True)
        else:
            self._private_log_warning("Container could not be started")
        return success

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

    def _private_get_local_ip_address(self) -> str:
        return netifaces.ifaddresses(self._private_configuration[self._private_configuration_section_general][self._private_configuration_section_general_key_networkinterface])[netifaces.AF_INET][0]['addr']

    def _private_commit(self, message: str, stage_all_changes: bool = True) -> None:
        repository = self._private_repository_folder
        commit_id = self._private_sc.git_commit(repository, message, self._private_adame_commit_author_name, "", stage_all_changes, True)
        remote_name = self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remotename]
        branch_name = self._private_securityconfiguration[self._private_securityconfiguration_section_general][self._private_configuration_section_general_key_remotebranch]
        remote_address = self._private_securityconfiguration.get(self._private_securityconfiguration_section_general, self._private_configuration_section_general_key_remoteaddress)
        self._private_log_information(f"Created commit {commit_id} in repository '{repository}' (commit-message: '{message}')", False, True, True)
        if self._private_remote_address_is_available:
            self._private_sc.git_add_or_set_remote_address(self._private_repository_folder, remote_name, remote_address)
            self._private_sc.git_push(self._private_repository_folder, remote_name, branch_name, branch_name, False, False)
            self._private_log_information(f"Pushed repository '{repository}' to remote remote_name ('{remote_address}')", False, True, True)
        else:
            self._private_log_warning("Either no remote-address is defined or the remote-address for the backup of the app-repository is not available.")

    def _private_name_to_docker_allowed_name(self, name: str) -> str:
        name = name.lower()
        return name

    def _private_start_program_asynchronously(self, program: str, argument: str, workingdirectory: str = None) -> int:
        self._private_log_information(f"Start program '{workingdirectory}>{program} {argument}' asynchronously", True)
        pid = self._private_sc.start_program_asynchronously(program, argument, workingdirectory)
        self._private_log_information(f"Started program has processid {pid}", True)
        return pid

    def _private_start_program_synchronously(self, program: str, argument: str, workingdirectory: str = None, expect_exitcode_zero: bool = True) -> list:
        workingdirectory = str_none_safe(workingdirectory)
        self._private_log_information(f"Start program '{workingdirectory}>{program} {argument}' synchronously", True)
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
-chmod (For setting up some permissions on the generated files)
-docker-compose (For starting and stopping Docker-container)
-git (For integrity)

Recommended commandline-commands:
-gpg (For checking the integrity of commits)
-kill (For killing snort)
-rsync (For exporting the log-files to a SIEM-server)
-ssh (Required for rsync)
-snort (For inspecting the network-traffic of the application)

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

    exportlogs_command_name = "exportlogs"
    exportlogs_parser = subparsers.add_parser(exportlogs_command_name)
    exportlogs_parser.add_argument("-c", "--configurationfile", required=True)

    diagnosis_command_name = "diagnosis"
    diagnosis_parser = subparsers.add_parser(diagnosis_command_name)
    diagnosis_parser.add_argument("-c", "--configurationfile", required=False)

    options = arger.parse_args()

    core = AdameCore()
    core.verbose = options.verbose

    if options.command == create_command_name:
        return core.create(options.name, options.folder, options.image, options.owner, options.gpgkey_of_owner)

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

    elif options.command == exportlogs_command_name:
        return core.exportlogs(options.configurationfile)

    elif options.command == diagnosis_command_name:
        return core.diagnosis(options.configurationfile)

    else:
        write_message_to_stdout(versioned_product_name)
        write_message_to_stdout(f"Run '{product_name} --help' to get help about the usage.")
        return 0

# </miscellaneous>


if __name__ == '__main__':
    adame_cli()
