import pytest
import unittest
import tempfile
import uuid
import os
from Adame.core import get_adame_version, AdameCore
from ScriptCollection.core import ensure_directory_does_not_exist, ensure_directory_exists


class TestEnvironment:
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
            test_environment = TestEnvironment()

            # act
            exit_code = test_environment.adameCore.create("myapplication", test_environment.folder, "httpd:latest", "owner")

            # assert
            assert exit_code == 0
            assert os.path.isfile(os.path.join(test_environment.folder, ".gitignore"))
            assert os.path.isfile(os.path.join(test_environment.folder, "ReadMe.md"))
            assert os.path.isfile(os.path.join(test_environment.folder, "License.txt"))
            assert os.path.isdir(os.path.join(test_environment.folder, ".git"))
            assert os.path.isdir(os.path.join(test_environment.folder, "Configuration"))
            assert os.path.isfile(os.path.join(test_environment.folder, "Configuration", "Adame.configuration"))
            assert os.path.isfile(os.path.join(test_environment.folder, "Configuration", "docker-compose.yml"))

        finally:
            test_environment.purge()

    def test_command_start(self):
        pass  # TODO implement test

    def test_command_stop(self):
        pass  # TODO implement test
