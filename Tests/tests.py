import pytest
import unittest
import tempfile
import uuid
import os
from Adame.core import get_adame_version, AdameCore
from ScriptCollection.core import ensure_directory_does_not_exist, ensure_directory_exists


class MiscellaneousTests(unittest.TestCase):

    def get_test_folder(self):
        result = os.path.join(tempfile.gettempdir(), "AdameTests", str(uuid.uuid4()))
        ensure_directory_exists(result)
        return result

    def test_adamecore_constructor_does_not_throw_any_exception(self):
        AdameCore()

    def test_command_create(self):
        core = AdameCore()
        folder = os.path.join(self.get_test_folder(), "folder")
        try:
            assert core.create("myapplication", folder, "httpd:latest", "owner") == 0
        finally:
            ensure_directory_does_not_exist(folder)

    def test_command_start(self):
        pass  # TODO implement test

    def test_command_stop(self):
        pass  # TODO implement test
