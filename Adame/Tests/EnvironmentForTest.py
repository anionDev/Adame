import tempfile
import uuid
import os
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
