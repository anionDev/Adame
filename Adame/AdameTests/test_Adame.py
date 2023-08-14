import unittest
import tempfile
import uuid
import os
import re
import shutil
from ScriptCollection.GeneralUtilities import GeneralUtilities
from ..Adame.Adame import Adame
from .EnvironmentForTest import EnvironmentForTest


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

        except Exception as e:
            GeneralUtilities.write_exception_to_stderr(e)
        finally:
            environment_for_test.dispose()

    def test_command_start(self):
        """UnitTest
Tests that the start-command works as expected"""

        # arrange
        environment_for_test = EnvironmentForTest()
        try:
            environment_for_test.create()
            # mock program calls which are maybe not available in a development-environment:
            environment_for_test.adame._internal_sc.register_mock_program_call("docker",  re.escape(
                f"compose --project-name {environment_for_test.adame._internal_get_container_name()} up --detach --build --quiet-pull " +
                "--force-recreate --always-recreate-deps"), re.escape(environment_for_test.adame._internal_configuration_folder), 0, "", "", 40)
            environment_for_test.adame._internal_sc.register_mock_program_call("snort", re.escape(
                f'-D -i eth0 -c "{environment_for_test.adame._internal_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame._internal_log_folder_for_ids}" ' +
                '-U -v -x -y -K ascii'), "", 0, "", "", 44)

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
        except Exception as e:
            GeneralUtilities.write_exception_to_stderr(e)
            raise e
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
            environment_for_test.adame._internal_sc.register_mock_program_call("docker",  re.escape(
                f"compose --project-name {environment_for_test.adame._internal_get_container_name()} up --detach --build --quiet-pull --force-recreate --always-recreate-deps"), re.escape(environment_for_test.adame._internal_configuration_folder), 0, "", "", 40)
            environment_for_test.adame._internal_sc.register_mock_program_call("snort", re.escape(
                f'-D -i eth0 -c "{environment_for_test.adame._internal_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame._internal_log_folder_for_ids}" -U -v -x -y -K ascii'), "", 0, "", "", 44)
            assert environment_for_test.adame.start(environment_for_test.adame_configuration_file) == 0

            assert environment_for_test.adame._internal_container_is_running()

            assert environment_for_test.adame._internal_ids_is_running()

            environment_for_test.adame.verify_no_pending_mock_process_queries()
            environment_for_test.adame._internal_sc.verify_no_pending_mock_program_calls()

            # mock program calls which are maybe not available in a development-environment:
            environment_for_test.adame._internal_sc.register_mock_program_call("docker",  re.escape(
                f"compose --project-name {environment_for_test.adame._internal_get_container_name()} down"), re.escape(environment_for_test.adame._internal_configuration_folder), 0, "", "", 68)
            environment_for_test.adame.register_mock_process_query(
                44, f'snort -D -i eth0 -c "{environment_for_test.adame._internal_networktrafficgeneratedrules_file}" -l "{environment_for_test.adame._internal_log_folder_for_ids}" -U -v -x -y -K ascii')
            environment_for_test.adame._internal_sc.register_mock_program_call("kill",  re.escape("-TERM 44"), "", 0, "", "", 72)
            environment_for_test.adame._internal_sc.register_mock_program_call("git",  ".*", ".*", 0, "", "", 40, 29)

            # act

            exitcode = environment_for_test.adame.stop(environment_for_test.adame_configuration_file)

            # assert

            assert exitcode == 0
            assert not environment_for_test.adame._internal_container_is_running()

        except Exception as e:
            GeneralUtilities.write_exception_to_stderr(e)
        finally:
            environment_for_test.dispose()

    def test_process_is_running(self):
        """RegressionTest
Ensures that adame._internal_process_is_running does not throw an exception when adame._internal_test_mode is false."""

        adame = Adame()
        adame.verbose = True
        adame.set_test_mode(False)
        assert not adame._internal_process_is_running(42, "test")

    def test_escape_git_folders_in_folder(self) -> None:
        # arrange
        adame = Adame()
        folder = os.path.join(tempfile.gettempdir(), str(uuid.uuid4()))
        renamed_items_file = os.path.join(folder, "renamings.csv")
        try:
            GeneralUtilities.ensure_directory_exists(folder)

            # folder
            # +-- a (folder)
            # |  +-- b1 (folder)
            # |  |   +-- .git (file)
            # |  +-- b2 (folder)
            # |      +-- .git (folder)
            # |          +-- head  (file)
            # +-- .git (folder)
            # |   +-- head (file)
            # +-- c
            #     +-- d1.gitd2.gitd3 (folder)
            # |       +-- head (file)

            folder_a = os.path.join(folder, "a")  # item 1
            folder_a_b1 = os.path.join(folder_a, "b1")  # item 2
            file_a_b1_git = os.path.join(folder_a_b1, ".git")  # item 3
            folder_a_b2 = os.path.join(folder_a, "b2")  # item 4
            folder_a_b2_git = os.path.join(folder_a_b2, ".git")  # item 5
            file_a_b2_git_head = os.path.join(folder_a_b2_git, "head")  # item 6
            folder_git = os.path.join(folder, ".git")  # item 7
            file_git_head = os.path.join(folder_git, "head")  # item 8
            folder_c = os.path.join(folder, "c")  # item 9
            folder_d = os.path.join(folder_c, "d.gitd.gitd")  # item 10
            file_c_d_head = os.path.join(folder_d, "head")  # item 11

            GeneralUtilities.ensure_directory_exists(folder_a)  # item 1
            GeneralUtilities.ensure_directory_exists(folder_a_b1)  # item 2
            GeneralUtilities.ensure_file_exists(file_a_b1_git)  # item 3
            GeneralUtilities.ensure_directory_exists(folder_a_b2)  # item 4
            GeneralUtilities.ensure_directory_exists(folder_a_b2_git)  # item 5
            GeneralUtilities.ensure_file_exists(file_a_b2_git_head)  # item 6
            GeneralUtilities.ensure_directory_exists(folder_git)  # item 7
            GeneralUtilities.ensure_file_exists(file_git_head)  # item 8
            GeneralUtilities.ensure_directory_exists(folder_c)  # item 9
            GeneralUtilities.ensure_directory_exists(folder_d)  # item 10
            GeneralUtilities.ensure_file_exists(file_c_d_head)  # item 11

            # act
            renamed_items = adame._internal_ensure_git_folder_are_escaped(folder, renamed_items_file)

            assert renamed_items is not None
            # TODO add assert for renamed items

            # assert
            assert os.path.isdir(folder_a)  # item 1
            assert os.path.isdir(folder_a_b1)  # item 2
            assert not os.path.isfile(file_a_b1_git)  # item 3
            assert os.path.isfile(file_a_b1_git+"x")  # item 3
            assert os.path.isdir(folder_a_b2)  # item 4
            assert not os.path.isdir(folder_a_b2_git)  # item 5
            assert os.path.isdir(folder_a_b2_git+"x")  # item 5
            assert not os.path.isfile(file_a_b2_git_head)  # item 6
            assert os.path.isfile(os.path.join(folder_a_b2_git+"x", "head"))  # item 6
            assert not os.path.isdir(folder_git)  # item 7
            assert os.path.isdir(folder_git+"x")  # item 7
            assert not os.path.isfile(file_git_head)  # item 8
            assert os.path.isfile(os.path.join(folder_git+"x", "head"))  # item 8
            assert os.path.isdir(folder_c)  # item 9
            assert not os.path.isdir(folder_d)  # item 10
            assert os.path.isdir(os.path.join(folder_c, "d.gitxd.gitxd"))  # item 10
            assert not os.path.isfile(file_c_d_head)  # item 11
            assert os.path.isfile(os.path.join(folder_c, "d.gitxd.gitxd", "head"))  # item 11

            # act
            adame._internal_ensure_git_folder_are_deescaped(folder, renamed_items_file)

            # assert
            assert os.path.isdir(folder_a)  # item 1
            assert os.path.isdir(folder_a_b1)  # item 2
            assert os.path.isfile(file_a_b1_git)  # item 3
            assert not os.path.isfile(file_a_b1_git+"x")  # item 3
            assert os.path.isdir(folder_a_b2)  # item 4
            assert os.path.isdir(folder_a_b2_git)  # item 5
            assert not os.path.isdir(folder_a_b2_git+"x")  # item 5
            assert os.path.isfile(file_a_b2_git_head)  # item 6
            assert not os.path.isfile(os.path.join(folder_a_b2_git+"x", "head"))  # item 6
            assert os.path.isdir(folder_git)  # item 7
            assert not os.path.isdir(folder_git+"x")  # item 7
            assert os.path.isfile(file_git_head)  # item 8
            assert not os.path.isfile(os.path.join(folder_git+"x", "head"))  # item 8
            assert os.path.isdir(folder_c)  # item 9
            assert os.path.isdir(folder_d)  # item 10
            assert not os.path.isdir(os.path.join(folder_c, "d.gitxd.gitxd"))  # item 10
            assert os.path.isfile(file_c_d_head)  # item 11
            assert not os.path.isfile(os.path.join(folder_c, "d.gitxd.gitxd", "head"))  # item 11

        finally:
            GeneralUtilities.ensure_directory_exists(folder)

    def test_create_demonstration_repository(self):
        """DemonstrationTest
Generates a simple adame-managed-repository as demonstration."""

        result_folder = GeneralUtilities.resolve_relative_path(
            f"..{os.path.sep}Other{os.path.sep}Reference{os.path.sep}ReferenceContent{os.path.sep}Examples{os.path.sep}NewRepository", os.path.dirname(os.path.realpath(__file__)))
        GeneralUtilities.ensure_directory_does_not_exist(result_folder)
        tests_folder = tempfile.gettempdir()+os.path.sep+str(uuid.uuid4())
        GeneralUtilities.ensure_directory_exists(tests_folder)
        environment_for_test = EnvironmentForTest(tests_folder)
        environment_for_test.adame.set_test_mode(True)
        environment_for_test.adame._internal_demo_mode = True
        environment_for_test.adame.verbose = True
        demoowner_name = "DemoOwner"
        environment_for_test.create("DemoApplication", demoowner_name)
        GeneralUtilities.ensure_directory_does_not_exist(f"{tests_folder}{os.path.sep}.git")
        shutil.copytree(tests_folder, result_folder)
        GeneralUtilities.ensure_directory_does_not_exist(tests_folder)
