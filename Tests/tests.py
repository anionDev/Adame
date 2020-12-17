import unittest
import tempfile
import uuid
import os
import re
from ScriptCollection.core import ensure_directory_does_not_exist, ensure_directory_exists, get_direct_files_of_folder, get_direct_folders_of_folder, file_is_empty
from Adame.core import AdameCore


class EnvironmentForTest:
    adame: AdameCore = None
    folder: str = None
    adame_configuration_file: str = None

    def __init__(self, folder=None):
        if(folder is None):
            folder = os.path.join(tempfile.gettempdir(), "AdameTests", str(uuid.uuid4()))
        ensure_directory_exists(folder)
        self.folder = folder
        self.adame = AdameCore()
        self.adame.verbose = True
        self.adame.set_test_mode(True)
        self.adame_configuration_file = os.path.join(self.folder, "Configuration", "Adame.configuration")

    def create(self, name = "myapplication", owner="owner"):
        self.adame._private_sc.mock_program_calls = False
        assert self.adame.create(name, self.folder, "httpd:latest", owner) == 0
        assert not self.adame._private_container_is_running()
        self.adame.set_test_mode(True)
        self.adame.verify_no_pending_mock_process_queries()
        self.adame._private_sc.verify_no_pending_mock_program_calls()

    def dispose(self):
        ensure_directory_does_not_exist(self.folder)
        self.adame.verify_no_pending_mock_process_queries()
        self.adame._private_sc.verify_no_pending_mock_program_calls()


class MiscellaneousTests(unittest.TestCase):

    def test_adamecore_constructor_does_not_throw_any_exception(self):
        """UnitTest
Tests that the constructor does not throw any exception"""

        AdameCore()

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
            assert len(get_direct_folders_of_folder(repository_folder)) == 3  # ".git", "Configuration", "Logs"
            assert len(get_direct_files_of_folder(repository_folder)) == 3

            assert os.path.isfile(os.path.join(repository_folder, ".gitignore"))
            assert os.path.isfile(os.path.join(repository_folder, "ReadMe.md"))
            assert os.path.isfile(os.path.join(repository_folder, "License.txt"))
            assert os.path.isdir(os.path.join(repository_folder, ".git"))

            log_folder = os.path.join(repository_folder, "Logs")
            assert os.path.isdir(log_folder)
            assert len(get_direct_folders_of_folder(log_folder)) == 3  # "Overhead", "Application", "IDS"
            assert len(get_direct_files_of_folder(log_folder)) == 0

            log_overhead_folder = os.path.join(log_folder, "Overhead")
            assert os.path.isdir(log_overhead_folder)
            assert len(get_direct_folders_of_folder(log_overhead_folder)) == 0
            overheadlogfiles = get_direct_files_of_folder(log_overhead_folder)
            assert len(overheadlogfiles) == 1
            assert not file_is_empty(overheadlogfiles[0])

            log_application_folder = os.path.join(log_folder, "Application")
            assert os.path.isdir(log_application_folder)
            assert len(get_direct_folders_of_folder(log_application_folder)) == 0
            assert len(get_direct_files_of_folder(log_application_folder)) == 0

            log_ids_folder = os.path.join(log_folder, "IDS")
            assert os.path.isdir(log_ids_folder)
            assert len(get_direct_folders_of_folder(log_ids_folder)) == 0
            assert len(get_direct_files_of_folder(log_ids_folder)) == 0

            configuration_folder = os.path.join(environment_for_test.folder,  "Configuration")
            assert os.path.isdir(configuration_folder)
            assert len(get_direct_folders_of_folder(configuration_folder)) == 1  # "Security"
            assert len(get_direct_files_of_folder(configuration_folder)) == 3
            adameconfigurationfile = os.path.join(configuration_folder, "Adame.configuration")
            assert os.path.isfile(adameconfigurationfile)
            assert not file_is_empty(adameconfigurationfile)
            dockercomposefile = os.path.join(configuration_folder, "docker-compose.yml")
            assert os.path.isfile(dockercomposefile)
            assert not file_is_empty(dockercomposefile)
            runninginformationfile = os.path.join(configuration_folder, "RunningInformation.txt")
            assert os.path.isfile(runninginformationfile)
            assert not file_is_empty(runninginformationfile)
            assert os.path.join(configuration_folder, "Adame.configuration") == environment_for_test.adame_configuration_file

            security_folder = os.path.join(configuration_folder, "Security")
            assert os.path.isdir(security_folder)
            assert len(get_direct_folders_of_folder(security_folder)) == 0
            assert len(get_direct_files_of_folder(security_folder)) == 4
            applicationprovidedscurityinformationfile = os.path.join(security_folder, "ApplicationProvidedSecurityInformation.xml")
            assert os.path.isfile(applicationprovidedscurityinformationfile)
            assert file_is_empty(applicationprovidedscurityinformationfile)
            networktrafficcustomrules = os.path.join(security_folder, "Networktraffic.Custom.rules")
            assert os.path.isfile(networktrafficcustomrules)
            assert file_is_empty(networktrafficcustomrules)
            networktrafficgeneratedrules = os.path.join(security_folder, "Networktraffic.Generated.rules")
            assert os.path.isfile(networktrafficgeneratedrules)
            assert file_is_empty(networktrafficgeneratedrules)
            securityconfigurationfile = os.path.join(security_folder, "Security.configuration")
            assert os.path.isfile(securityconfigurationfile)
            assert not file_is_empty(securityconfigurationfile)

        finally:
            environment_for_test.dispose()

    def test_command_start(self):
        """UnitTest
Tests that the start-command works as expected"""

        try:

            # arrange

            environment_for_test = EnvironmentForTest()
            environment_for_test.create()

            environment_for_test.adame._private_sc.register_mock_program_call("docker-compose",  re.escape("up --detach --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps"), re.escape(environment_for_test.adame._private_configuration_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("snort", re.escape(f'-D -i eth0 -c "{environment_for_test.adame._private_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame._private_log_folder_for_ids}" -U -v -x -y -K ascii'), "", 0, "", "", 44)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "reset", re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 52)
            environment_for_test.adame._private_sc.register_mock_program_call("git", f'stage -- "{re.escape(environment_for_test.adame._private_running_information_file)}"', re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 56)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "diff", re.escape(environment_for_test.adame._private_repository_folder), 0, "(some diff content)", "", 60)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('commit --message="Started container (Container-process: True; IDS-process: True)" --author="Adame <>" --allow-empty'), re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 64)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('rev-parse --verify HEAD'), re.escape(environment_for_test.adame._private_repository_folder), 0, "3c5a38ad96d0acf5e2822bbcd655387b42352cb0", "", 64)

            # act

            exitcode = environment_for_test.adame.start(environment_for_test.adame_configuration_file)

            # assert

            assert exitcode == 0
            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._private_sc.verify_no_pending_mock_program_calls()

            assert environment_for_test.adame._private_container_is_running()
            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._private_sc.verify_no_pending_mock_program_calls()

            assert environment_for_test.adame._private_ids_is_running()
            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._private_sc.verify_no_pending_mock_program_calls()

        finally:
            environment_for_test.dispose()

    def test_command_stop(self):
        """UnitTest
Tests that the stop-command works as expected"""

        try:

            # arrange

            environment_for_test = EnvironmentForTest()
            environment_for_test.create()

            environment_for_test.adame._private_sc.register_mock_program_call("docker-compose",  re.escape("up --detach --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps"), re.escape(environment_for_test.adame._private_configuration_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("snort", re.escape(f'-D -i eth0 -c "{environment_for_test.adame._private_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame._private_log_folder_for_ids}" -U -v -x -y -K ascii'), "", 0, "", "", 44)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "reset", re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 52)
            environment_for_test.adame._private_sc.register_mock_program_call("git", f'stage -- "{re.escape(environment_for_test.adame._private_running_information_file)}"', re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 56)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "diff", re.escape(environment_for_test.adame._private_repository_folder), 0, "(some diff content)", "", 60)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('commit --message="Started container (Container-process: True; IDS-process: True)" --author="Adame <>" --allow-empty'), re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 64)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('rev-parse --verify HEAD'), re.escape(environment_for_test.adame._private_repository_folder), 0, "3c5a38ad96d0acf5e2822bbcd655387b42352cb0", "", 68)
            assert environment_for_test.adame.start(environment_for_test.adame_configuration_file) == 0

            assert environment_for_test.adame._private_container_is_running()

            assert environment_for_test.adame._private_ids_is_running()

            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._private_sc.verify_no_pending_mock_program_calls()

            environment_for_test.adame._private_sc.register_mock_program_call("git", "reset", re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("git", f'stage -- "{re.escape(environment_for_test.adame._private_running_information_file)}"', re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 48)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "diff", re.escape(environment_for_test.adame._private_repository_folder), 0, "(some diff content)", "", 52)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('commit --message="Stopped container (Container-process: False; IDS-process: False)" --author="Adame <>" --allow-empty'), re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 56)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('rev-parse --verify HEAD'), re.escape(environment_for_test.adame._private_repository_folder), 0, "4d6a38ad96d0acf5e2822bbcd655387b42352cc1", "", 60)

            environment_for_test.adame._private_sc.register_mock_program_call("docker-compose",  re.escape("down --remove-orphans"), re.escape(environment_for_test.adame._private_configuration_folder), 0, "", "", 68)

            environment_for_test.adame.register_mock_process_query(44, f'snort -D -i eth0 -c "{environment_for_test.adame._private_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame._private_log_folder_for_ids}" -U -v -x -y -K ascii')
            environment_for_test.adame._private_sc.register_mock_program_call("kill",  re.escape("-TERM 44"), "", 0, "", "", 72)

            # act

            exitcode = environment_for_test.adame.stop(environment_for_test.adame_configuration_file)

            # assert

            assert exitcode == 0
            assert not environment_for_test.adame._private_container_is_running()

        finally:
            environment_for_test.dispose()

    def test_process_is_running(self):
        """RegressionTest
Ensures that adame._private_process_is_running does not throw an exception when adame._private_test_mode is false."""

        adame = AdameCore()
        adame.verbose = True
        adame.set_test_mode(False)
        assert not adame._private_process_is_running(42, "test")

    def test_create_demonstration_repository(self):
        """DemonstrationTest
Generates a simple adame-managed-repository as demonstration."""

        tests_folder = f"{os.path.dirname(os.path.realpath(__file__))}{os.path.sep}..{os.path.sep}Reference{os.path.sep}Examples{os.path.sep}NewRepository"
        ensure_directory_does_not_exist(tests_folder)
        environment_for_test = EnvironmentForTest(tests_folder)
        environment_for_test.adame._private_demo_mode=True
        environment_for_test.create("DemoApplication","DemoOwner")
        ensure_directory_does_not_exist(f"{tests_folder}{os.path.sep}.git")
