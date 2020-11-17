import unittest
import tempfile
import uuid
import os
import re
from ScriptCollection.core import ensure_directory_does_not_exist, ensure_directory_exists
from Adame.core import AdameCore


class EnvironmentForTest:
    adame: AdameCore = None
    folder: str = None
    adame_configuration_file: str = None

    def __init__(self):
        folder = os.path.join(tempfile.gettempdir(), "AdameTests", str(uuid.uuid4()))
        ensure_directory_exists(folder)
        self.folder = folder
        self.adame = AdameCore()
        self.adame.verbose = True
        self.adame.set_test_mode(True)
        self.adame_configuration_file = os.path.join(self.folder, "Configuration", "Adame.configuration")

    def create(self):
        self.adame._private_sc.mock_program_calls = False
        assert self.adame.create("myapplication", self.folder, "httpd:latest", "owner") == 0
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

            assert os.path.isfile(os.path.join(environment_for_test.folder, ".gitignore"))
            assert os.path.isfile(os.path.join(environment_for_test.folder, "ReadMe.md"))
            assert os.path.isfile(os.path.join(environment_for_test.folder, "License.txt"))
            assert os.path.isdir(os.path.join(environment_for_test.folder, ".git"))
            assert os.path.isdir(os.path.join(environment_for_test.folder, "Configuration"))
            assert os.path.isdir(os.path.join(environment_for_test.folder, f"Logs{os.path.sep}Overhead"))
            assert os.path.isdir(os.path.join(environment_for_test.folder, f"Logs{os.path.sep}Application"))
            assert os.path.isdir(os.path.join(environment_for_test.folder, f"Logs{os.path.sep}IDS"))
            assert os.path.join(environment_for_test.folder, "Configuration", "Adame.configuration") == environment_for_test.adame_configuration_file
            assert os.path.isfile(os.path.join(environment_for_test.folder, "Configuration", "Adame.configuration"))
            assert os.path.isfile(os.path.join(environment_for_test.folder, "Configuration", "docker-compose.yml"))

        finally:
            environment_for_test.dispose()

    def test_command_start(self):
        """UnitTest
Tests that the start-command works as expected"""

        try:

            # arrange

            environment_for_test = EnvironmentForTest()
            environment_for_test.create()

            environment_for_test.adame._private_sc.register_mock_program_call("docker-compose",  re.escape("up --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps"), re.escape(environment_for_test.adame._private_configuration_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("snort", re.escape(f'-c "{environment_for_test.adame._private_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame._private_log_folder_for_ids}"'), "", 0, "", "", 44)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "reset", re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("git", f'stage -- "{re.escape(environment_for_test.adame._private_running_information_file)}"', re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 48)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "diff", re.escape(environment_for_test.adame._private_repository_folder), 0, "(some diff content)", "", 52)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('commit --message="Started container (Container-process: 40; IDS-process: 44)" --author="Adame <>"'), re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 56)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('rev-parse --verify HEAD'), re.escape(environment_for_test.adame._private_repository_folder), 0, "3c5a38ad96d0acf5e2822bbcd655387b42352cb0", "", 60)

            # act

            exitcode = environment_for_test.adame.start(environment_for_test.adame_configuration_file)

            # assert

            assert exitcode == 0
            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._private_sc.verify_no_pending_mock_program_calls()

            environment_for_test.adame.register_mock_process_query(40, "docker-compose")
            assert environment_for_test.adame._private_container_is_running()
            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._private_sc.verify_no_pending_mock_program_calls()

            environment_for_test.adame.register_mock_process_query(44, "snort")
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

            environment_for_test.adame._private_sc.register_mock_program_call("docker-compose",  re.escape("up --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps"), re.escape(environment_for_test.adame._private_configuration_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("snort", re.escape(f'-c "{environment_for_test.adame._private_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame._private_log_folder_for_ids}"'), "", 0, "", "", 44)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "reset", re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("git", f'stage -- "{re.escape(environment_for_test.adame._private_running_information_file)}"', re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 48)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "diff", re.escape(environment_for_test.adame._private_repository_folder), 0, "(some diff content)", "", 52)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('commit --message="Started container (Container-process: 40; IDS-process: 44)" --author="Adame <>"'), re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 56)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('rev-parse --verify HEAD'), re.escape(environment_for_test.adame._private_repository_folder), 0, "3c5a38ad96d0acf5e2822bbcd655387b42352cb0", "", 60)
            assert environment_for_test.adame.start(environment_for_test.adame_configuration_file) == 0

            environment_for_test.adame.register_mock_process_query(40, "docker-compose")
            assert environment_for_test.adame._private_container_is_running()

            environment_for_test.adame.register_mock_process_query(44, "snort")
            assert environment_for_test.adame._private_ids_is_running()

            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._private_sc.verify_no_pending_mock_program_calls()

            environment_for_test.adame._private_sc.register_mock_program_call("git", "reset", re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("git", f'stage -- "{re.escape(environment_for_test.adame._private_running_information_file)}"', re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 48)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "diff", re.escape(environment_for_test.adame._private_repository_folder), 0, "(some diff content)", "", 52)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('commit --message="Stopped container (Container-process: ; IDS-process: )" --author="Adame <>"'), re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 56)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('rev-parse --verify HEAD'), re.escape(environment_for_test.adame._private_repository_folder), 0, "4d6a38ad96d0acf5e2822bbcd655387b42352cc1", "", 60)

            environment_for_test.adame._private_sc.register_mock_program_call("docker-compose",  re.escape("down --remove-orphans"), re.escape(environment_for_test.adame._private_configuration_folder), 0, "", "", 68)
            environment_for_test.adame._private_sc.register_mock_program_call("kill",  re.escape("44"), "", 0, "", "", 72)
            environment_for_test.adame.register_mock_process_query(40, "docker-compose")
            environment_for_test.adame.register_mock_process_query(44, "snort")

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
        adame.verbose=True
        adame.set_test_mode(False)
        assert not adame._private_process_is_running(42, "test")
