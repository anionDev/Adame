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
        self.adame._private_sc.mock_program_calls = True

    def dispose(self):
        ensure_directory_does_not_exist(self.folder)
        self.adame.verify_no_pending_mock_process_queries()
        self.adame._private_sc.verify_no_pending_mock_program_calls()


class MiscellaneousTests(unittest.TestCase):

    def test_adamecore_constructor_does_not_throw_any_exception(self):
        AdameCore()

    def test_command_create_test_environment(self):

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
        try:

            # arrange
            environment_for_test = EnvironmentForTest()
            environment_for_test.create()
            environment_for_test.adame._private_sc.register_mock_program_call("docker-compose",  re.escape("up --build --quiet-pull --remove-orphans --force-recreate --always-recreate-deps"), re.escape(environment_for_test.adame._private_configuration_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("snort", re.escape(f'-c "{environment_for_test.adame._private_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame._private_log_folder_for_intrusiondetectionsystem}"'), "", 0, "", "", 44)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "reset", re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 40)
            environment_for_test.adame._private_sc.register_mock_program_call("git", f'stage -- "{re.escape(environment_for_test.adame._private_running_information_file)}"', re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 48)
            environment_for_test.adame._private_sc.register_mock_program_call("git", "diff", re.escape(environment_for_test.adame._private_repository_folder), 0, "(some diff content)", "", 52)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('commit --message="Started container (Container-process: 40; IDS-process: 44)" --author="Adame <>"'), re.escape(environment_for_test.adame._private_repository_folder), 0, "", "", 56)
            environment_for_test.adame._private_sc.register_mock_program_call("git", re.escape('rev-parse --verify HEAD'), re.escape(environment_for_test.adame._private_repository_folder), 0, "3c5a38ad96d0acf5e2822bbcd655387b42352cb0", "", 60)
            environment_for_test.adame.register_mock_process_query(40, "docker-compose")
            environment_for_test.adame.register_mock_process_query(44, "snort")

            # act
            exit_code = environment_for_test.adame.start(environment_for_test.adame_configuration_file)

            # assert
            assert exit_code == 0
            assert environment_for_test.adame._private_container_is_running()
            assert environment_for_test.adame._private_intrusion_detection_is_running()

        finally:
            environment_for_test.dispose()

    def test_command_stop(self):
        try:

            # arrange
            environment_for_test = EnvironmentForTest()
            environment_for_test.create()
            assert environment_for_test.adame.start(environment_for_test.adame_configuration_file) == 0
            assert environment_for_test.adame._private_container_is_running()

            # act
            exit_code = environment_for_test.adame.stop(environment_for_test.adame_configuration_file)

            # assert
            assert exit_code == 0
            assert not environment_for_test.adame._private_container_is_running()

        finally:
            environment_for_test.dispose()

    def test_command_diagnosis_with_configurationfile(self):
        try:

            # arrange
            environment_for_test = EnvironmentForTest()

            # act
            exit_code = environment_for_test.adame.diagnosis(environment_for_test.adame_configuration_file)

            # assert
            assert exit_code == 0

        finally:
            environment_for_test.dispose()

    def test_command_diagnosis_without_configurationfile(self):
        try:

            # arrange
            environment_for_test = EnvironmentForTest()
            environment_for_test.adame.adame_configuration_file = None

            # act
            exit_code = environment_for_test.adame.diagnosis(None)

            # assert
            assert exit_code == 0

        finally:
            environment_for_test.dispose()
