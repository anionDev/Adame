import pytest
import unittest
import tempfile
import uuid
import os
from Adame.core import get_adame_version, AdameCore
from ScriptCollection.core import ensure_directory_does_not_exist, ensure_directory_exists


class EnvironmentForTest:
    adameCore: AdameCore = None
    folder: str = None

    def __init__(self):

        folder = os.path.join(tempfile.gettempdir(), "AdameTests", str(uuid.uuid4()))
        ensure_directory_exists(folder)
        self.folder = folder
        self.adameCore = AdameCore()

    def purge(self):
        ensure_directory_does_not_exist(self.folder)


class MiscellaneousTests(unittest.TestCase):

    def test_adamecore_constructor_does_not_throw_any_exception(self):
        AdameCore()

    def test_command_create(self):
        try:

            # arrange
            environment_for_test = EnvironmentForTest()

            # act
            exit_code = environment_for_test.adameCore.create("myapplication", environment_for_test.folder, "httpd:latest", "owner")

            # assert
            assert exit_code == 0
            assert os.path.isfile(os.path.join(environment_for_test.folder, ".gitignore"))
            assert os.path.isfile(os.path.join(environment_for_test.folder, "ReadMe.md"))
            assert os.path.isfile(os.path.join(environment_for_test.folder, "License.txt"))
            assert os.path.isdir(os.path.join(environment_for_test.folder, ".git"))
            assert os.path.isdir(os.path.join(environment_for_test.folder, "Configuration"))
            assert os.path.isfile(os.path.join(environment_for_test.folder, "Configuration", "Adame.configuration"))
            assert os.path.isfile(os.path.join(environment_for_test.folder, "Configuration", "docker-compose.yml"))

        finally:
            environment_for_test.purge()

    def test_command_start(self):
        pass  # TODO implement test

    def test_command_stop(self):
        pass  # TODO implement test
