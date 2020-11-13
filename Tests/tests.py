import unittest
import tempfile
import uuid
import os
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
        self.adame._private_check_privileges = False
        self.adame_configuration_file = os.path.join(self.folder, "Configuration", "Adame.configuration")

    def create(self):
        assert self.adame.create("myapplication", self.folder, "httpd:latest", "owner") == 0
        assert not self.adame._private_container_is_running()
        self.adame._private_sc.mock_program_calls = True

    def purge(self):
        if(not (self.adame_configuration_file is None)):
            self.adame.stop(self.adame_configuration_file)
            assert not self.adame._private_container_is_running()
        ensure_directory_does_not_exist(self.folder)
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
            assert os.path.join(environment_for_test.folder, "Configuration", "Adame.configuration") == environment_for_test.adame_configuration_file
            assert os.path.isfile(os.path.join(environment_for_test.folder, "Configuration", "Adame.configuration"))
            assert os.path.isfile(os.path.join(environment_for_test.folder, "Configuration", "docker-compose.yml"))

        finally:
            environment_for_test.purge()

    def test_command_start(self):
        try:

            # arrange
            environment_for_test = EnvironmentForTest()
            environment_for_test.create()
            environment_for_test.adame._private_sc.register_mock_programm_call("", "", "", 0, "", "", 0) # TODO register program-calls

            # act
            exit_code = environment_for_test.adame.start(environment_for_test.adame_configuration_file)

            # assert
            assert environment_for_test.adame._private_container_is_running()
            assert exit_code == 0

        finally:
            environment_for_test.purge()

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
            assert not environment_for_test.adame._private_container_is_running()
            assert exit_code == 0

        finally:
            environment_for_test.purge()

    def test_command_diagnosis_with_configurationfile(self):
        try:

            # arrange
            environment_for_test = EnvironmentForTest()

            # act
            exit_code = environment_for_test.adame.diagnosis(environment_for_test.adame_configuration_file)

            # assert
            assert exit_code == 0

        finally:
            environment_for_test.purge()

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
            environment_for_test.purge()
