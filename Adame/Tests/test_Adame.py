import unittest
import tempfile
import uuid
import os
import re
from distutils.dir_util import copy_tree
from ScriptCollection.GeneralUtilities import GeneralUtilities
from ..Adame import Adame


class EnvironmentForTest:
    adame: Adame = None
    folder: str = None
    adame_configuration_file: str = None

    def __init__(self, folder=None):
        if(folder is None):
            folder = os.path.join(tempfile.gettempdir(), "AdameTests", str(uuid.uuid4()))
        GeneralUtilities.ensure_directory_exists(folder)
        self.folder = folder
        self.adame = Adame()
        self.adame.verbose = True
        self.adame.set_test_mode(True)
        self.adame_configuration_file = os.path.join(self.folder, "Configuration", "Adame.configuration")

    def create(self, name="myapplication", owner="owner"):
        self.adame._internal_sc.mock_program_calls = False
        assert self.adame.create(name, self.folder, "httpd:latest", owner) == 0
        assert not self.adame._internal_container_is_running()
        self.adame.set_test_mode(True)
        self.adame.verify_no_pending_mock_process_queries()
        self.adame._internal_sc.verify_no_pending_mock_program_calls()

    def dispose(self):
        GeneralUtilities.ensure_directory_does_not_exist(self.folder)
        self.adame.verify_no_pending_mock_process_queries()
        self.adame._internal_sc.verify_no_pending_mock_program_calls()


class AdameTests(unittest.TestCase):

    def test_adamecore_constructor_does_not_throw_any_exception(self):
        """UnitTest
Tests that the constructor does not throw any exception"""

        Adame()

    def test_command_create(self):
        """UnitTest
Tests that the create-command works as expected"""

        try:

            # arrange

            environment_for_test = EnvironmentForTest()

            # act

            environment_for_test.create()

            # assert

            repository_folder = environment_for_test.folder
            assert os.path.isdir(repository_folder)
            assert len(GeneralUtilities.get_direct_folders_of_folder(repository_folder)) == 3  # ".git", "Configuration", "Logs"
            assert len(GeneralUtilities.get_direct_files_of_folder(repository_folder)) == 3

            assert os.path.isfile(os.path.join(repository_folder, ".gitignore"))
            assert os.path.isfile(os.path.join(repository_folder, "ReadMe.md"))
            assert os.path.isfile(os.path.join(repository_folder, "License.txt"))
            assert os.path.isdir(os.path.join(repository_folder, ".git"))

            log_folder = os.path.join(repository_folder, "Logs")
            assert os.path.isdir(log_folder)
            assert len(GeneralUtilities.get_direct_folders_of_folder(log_folder)) == 3  # "Overhead", "Application", "IDS"
            assert len(GeneralUtilities.get_direct_files_of_folder(log_folder)) == 0

            log_overhead_folder = os.path.join(log_folder, "Overhead")
            assert os.path.isdir(log_overhead_folder)
            assert len(GeneralUtilities.get_direct_folders_of_folder(log_overhead_folder)) == 0
            overheadlogfiles = GeneralUtilities.get_direct_files_of_folder(log_overhead_folder)
            assert len(overheadlogfiles) == 2
            gitkeep_file = overheadlogfiles[0]
            assert gitkeep_file == os.path.join(log_overhead_folder, ".gitkeep")
            assert GeneralUtilities.file_is_empty(gitkeep_file)
            assert not GeneralUtilities.file_is_empty(overheadlogfiles[1])

            log_application_folder = os.path.join(log_folder, "Application")
            assert os.path.isdir(log_application_folder)
            assert len(GeneralUtilities.get_direct_folders_of_folder(log_application_folder)) == 0
            application_logfiles = GeneralUtilities.get_direct_files_of_folder(log_application_folder)
            assert len(application_logfiles) == 1  # ".gitkeep"
            assert GeneralUtilities.file_is_empty(application_logfiles[0])

            log_ids_folder = os.path.join(log_folder, "IDS")
            assert os.path.isdir(log_ids_folder)
            assert len(GeneralUtilities.get_direct_folders_of_folder(log_ids_folder)) == 0
            ids_logfiles = GeneralUtilities.get_direct_files_of_folder(log_ids_folder)
            assert len(ids_logfiles) == 1  # ".gitkeep"
            assert GeneralUtilities.file_is_empty(ids_logfiles[0])

            configuration_folder = os.path.join(environment_for_test.folder,  "Configuration")
            assert os.path.isdir(configuration_folder)
            assert len(GeneralUtilities.get_direct_folders_of_folder(configuration_folder)) == 1  # "Security"
            assert len(GeneralUtilities.get_direct_files_of_folder(configuration_folder)) == 5
            adameconfigurationfile = os.path.join(configuration_folder, "Adame.configuration")
            assert os.path.isfile(adameconfigurationfile)
            assert not GeneralUtilities.file_is_empty(adameconfigurationfile)
            dockercomposefile = os.path.join(configuration_folder, "docker-compose.yml")
            assert os.path.isfile(dockercomposefile)
            assert not GeneralUtilities.file_is_empty(dockercomposefile)
            runninginformationfile = os.path.join(configuration_folder, "RunningInformation.txt")
            assert os.path.isfile(runninginformationfile)
            assert not GeneralUtilities.file_is_empty(runninginformationfile)
            assert os.path.join(configuration_folder, "Adame.configuration") == environment_for_test.adame_configuration_file
            dockercomposefile = os.path.join(configuration_folder, ".gitconfig")
            assert os.path.isfile(dockercomposefile)
            assert not GeneralUtilities.file_is_empty(dockercomposefile)
            dockercomposefile = os.path.join(configuration_folder, "FileMetadata.csv")
            assert os.path.isfile(dockercomposefile)
            assert not GeneralUtilities.file_is_empty(dockercomposefile)

            security_folder = os.path.join(configuration_folder, "Security")
            assert os.path.isdir(security_folder)
            assert len(GeneralUtilities.get_direct_folders_of_folder(security_folder)) == 0
            assert len(GeneralUtilities.get_direct_files_of_folder(security_folder)) == 4
            applicationprovidedscurityinformationfile = os.path.join(security_folder, "ApplicationProvidedSecurityInformation.xml")
            assert os.path.isfile(applicationprovidedscurityinformationfile)
            assert GeneralUtilities.file_is_empty(applicationprovidedscurityinformationfile)
            networktrafficcustomrules = os.path.join(security_folder, "Networktraffic.Custom.rules")
            assert os.path.isfile(networktrafficcustomrules)
            assert GeneralUtilities.file_is_empty(networktrafficcustomrules)
            networktrafficgeneratedrules = os.path.join(security_folder, "Networktraffic.Generated.rules")
            assert os.path.isfile(networktrafficgeneratedrules)
            assert GeneralUtilities.file_is_empty(networktrafficgeneratedrules)
            securityconfigurationfile = os.path.join(security_folder, "Security.configuration")
            assert os.path.isfile(securityconfigurationfile)
            assert not GeneralUtilities.file_is_empty(securityconfigurationfile)

        finally:
            environment_for_test.dispose()

    def test_command_start(self):
        """UnitTest
Tests that the start-command works as expected"""

        try:

            # arrange

            environment_for_test = EnvironmentForTest()
            environment_for_test.create()
            # mock program calls which are maybe not available in a development-environment:
            environment_for_test.adame._internal_sc.register_mock_program_call("docker-compose",  re.escape(f"--project-name {environment_for_test.adame._internal_get_container_name()} up --detach --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps"), re.escape(environment_for_test.adame.__internal_configuration_folder), 0, "", "", 40)
            environment_for_test.adame._internal_sc.register_mock_program_call("snort", re.escape(f'-D -i eth0 -c "{environment_for_test.adame.__internal_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame.__internal_log_folder_for_ids}" -U -v -x -y -K ascii'), "", 0, "", "", 44)

            # act

            exitcode = environment_for_test.adame.start(environment_for_test.adame_configuration_file)

            # assert

            assert exitcode == 0
            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._internal_sc.verify_no_pending_mock_program_calls()

            assert environment_for_test.adame._internal_container_is_running()
            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._internal_sc.verify_no_pending_mock_program_calls()

            assert environment_for_test.adame._internal_ids_is_running()
            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._internal_sc.verify_no_pending_mock_program_calls()

        finally:
            environment_for_test.dispose()

    def test_command_stop(self):
        """UnitTest
Tests that the stop-command works as expected"""

        try:

            # arrange

            environment_for_test = EnvironmentForTest()
            environment_for_test.create()
            # mock program calls which are maybe not available in a development-environment:
            environment_for_test.adame._internal_sc.register_mock_program_call("docker-compose",  re.escape(f"--project-name {environment_for_test.adame._internal_get_container_name()} up --detach --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps"), re.escape(environment_for_test.adame.__internal_configuration_folder), 0, "", "", 40)
            environment_for_test.adame._internal_sc.register_mock_program_call("snort", re.escape(f'-D -i eth0 -c "{environment_for_test.adame.__internal_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame.__internal_log_folder_for_ids}" -U -v -x -y -K ascii'), "", 0, "", "", 44)
            assert environment_for_test.adame.start(environment_for_test.adame_configuration_file) == 0

            assert environment_for_test.adame._internal_container_is_running()

            assert environment_for_test.adame._internal_ids_is_running()

            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._internal_sc.verify_no_pending_mock_program_calls()

            # mock program calls which are maybe not available in a development-environment:
            environment_for_test.adame._internal_sc.register_mock_program_call("docker-compose",  re.escape(f"--project-name {environment_for_test.adame._internal_get_container_name()} down --remove-orphans"), re.escape(environment_for_test.adame.__internal_configuration_folder), 0, "", "", 68)
            environment_for_test.adame.register_mock_process_query(44, f'snort -D -i eth0 -c "{environment_for_test.adame.__internal_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame.__internal_log_folder_for_ids}" -U -v -x -y -K ascii')
            environment_for_test.adame._internal_sc.register_mock_program_call("kill",  re.escape("-TERM 44"), "", 0, "", "", 72)

            # act

            exitcode = environment_for_test.adame.stop(environment_for_test.adame_configuration_file)

            # assert

            assert exitcode == 0
            assert not environment_for_test.adame._internal_container_is_running()

        finally:
            environment_for_test.dispose()

    def test_process_is_running(self):
        """RegressionTest
Ensures that adame._internal_process_is_running does not throw an exception when adame._internal_test_mode is false."""

        adame = Adame()
        adame.verbose = True
        adame.set_test_mode(False)
        assert not adame._internal_process_is_running(42, "test")

    def test_create_demonstration_repository(self):
        """DemonstrationTest
Generates a simple adame-managed-repository as demonstration."""

        result_folder = GeneralUtilities.resolve_relative_path(
            f"..{os.path.sep}..{os.path.sep}Reference{os.path.sep}Examples{os.path.sep}NewRepository", os.path.dirname(os.path.realpath(__file__)))
        GeneralUtilities.ensure_directory_does_not_exist(result_folder)
        GeneralUtilities.ensure_directory_exists(result_folder)
        tests_folder = tempfile.gettempdir()+os.path.sep+str(uuid.uuid4())
        GeneralUtilities.ensure_directory_exists(tests_folder)
        environment_for_test = EnvironmentForTest(tests_folder)
        environment_for_test.adame.set_test_mode(True)
        environment_for_test.adame._internal_demo_mode = True
        environment_for_test.adame.verbose = True
        demoowner_name = "DemoOwner"
        environment_for_test.create("DemoApplication", demoowner_name)
        GeneralUtilities.ensure_directory_does_not_exist(f"{tests_folder}{os.path.sep}.git")
        copy_tree(tests_folder, result_folder)
        GeneralUtilities.ensure_directory_does_not_exist(tests_folder)
