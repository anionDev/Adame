import argparse
from argparse import RawTextHelpFormatter
from ScriptCollection.core import write_message_to_stdout, write_message_to_stderr, write_exception_to_stderr_with_traceback, write_exception_to_stderr, git_commit, execute_and_raise_exception_if_exit_code_is_not_zero, write_text_to_file, ensure_directory_exists, resolve_relative_path_from_current_working_directory
import sys
import traceback
import configparser
import os
from configparser import ConfigParser

version = "0.2.2"


class AdameCore(object):

    # <constants>

    _adame_commit_author_name = "Adame"
    _adame_commit_author_email = "marius.goecke@gmail.com"
    _configuration_section_general = "general"
    _configuration_section_general_key_name = "name"
    _configuration_section_general_key_folder = "folder"
    _configuration_section_general_key_image = "image"
    _configuration_section_general_key_owner = "owner"
    _configuration_section_general_key_dockercomposefile = "dockercomposefile"

    # </constants>

    # <properties>

    verbose = False
    encoding = "utf-8"

    # </properties>

    # <initialization>

    def __init__(self):
        pass

    # </initialization>

    # <create_new_environment-command>

    def create_new_environment(self, name: str, folder: str, image: str, owner: str):
        if(self.verbose):
            write_message_to_stdout(f"{self._configuration_section_general_key_name}: {name}")
            write_message_to_stdout(f"{self._configuration_section_general_key_folder}: {folder}")
            write_message_to_stdout(f"{self._configuration_section_general_key_image}: {image}")
            write_message_to_stdout(f"{self._configuration_section_general_key_owner}: {owner}")
        return self._private_execute_task("Create new environment", lambda: self._private_create_new_environment(name, folder, image, owner))

    def _private_create_new_environment(self, name: str, folder: str, image: str, owner: str):
        configurationfile = os.path.join(folder, "Adame.configuration")
        config = configparser.ConfigParser()

        ensure_directory_exists(folder)
        config[self._configuration_section_general][self._configuration_section_general_key_name] = name
        config[self._configuration_section_general][self._configuration_section_general_key_folder] = folder
        config[self._configuration_section_general][self._configuration_section_general_key_image] = image
        config[self._configuration_section_general][self._configuration_section_general_key_owner] = owner
        config[self._configuration_section_general][self._configuration_section_general_key_dockercomposefile] = os.path.join(folder, "docker-compose.yml")
        with open(configurationfile, 'w+', encoding=self.encoding) as configfile:
            config.write(configfile)
        if(self.verbose):
            write_message_to_stdout(f"Created file '{configfile}'")

        self.create_file_in_repository(folder, "ReadMe.md", self.get_readme_file_content(config))
        self.create_file_in_repository(folder, "License.txt", self.get_license_file_content(config))
        self.create_file_in_repository(folder, ".gitignore", self.get_gitignore_file_content(config))

        execute_and_raise_exception_if_exit_code_is_not_zero("git", "init", folder)

        self._private_commit(folder, f"Initial commit for Adame app-repository of {name}")

        return 0

    # </create_new_environment-command>

    # <start_environment-command>

    def start_environment(self, configurationfile: str):
        if(self.verbose):
            write_message_to_stdout(f"configurationfile: '{configurationfile}'")
        return self._private_execute_task("Start environment", lambda: self._private_start_environment(configurationfile))

    def _private_start_environment(self, configurationfile: str):
        configuration = configparser.ConfigParser()
        configuration.read(configurationfile)
        if(not self._private_container_is_running(configurationfile)):
            self._private_start_container(configuration)
        return 0

    # </start_environment-command>

    # <stop_environment-command>

    def stop_environment(self, configurationfile: str):
        if(self.verbose):
            write_message_to_stdout(f"configurationfile: '{configurationfile}'")
        return self._private_execute_task("Stop environment", lambda: self._private_stop_environment(configurationfile))

    def _private_stop_environment(self, configurationfile: str):
        configuration = configparser.ConfigParser()
        configuration.read(configurationfile)
        if(self._private_container_is_running(configurationfile)):
            self._private_stop_container(configuration)
        return 0

    # </stop_environment-command>

    # <applyconfiguration-command>

    def applyconfiguration(self, configurationfile: str):
        if(self.verbose):
            write_message_to_stdout(f"configurationfile: '{configurationfile}'")
        return self._private_execute_task("Apply configuration", lambda: self._private_applyconfiguration(configurationfile))

    def _private_applyconfiguration(self, configurationfile: str):
        configuration = configparser.ConfigParser()
        configuration.read(configurationfile)
        write_text_to_file(configuration.get(self._configuration_section_general, self._configuration_section_general_key_dockercomposefile), self.get_dockercompose_file_content(configuration), self.encoding)
        # self._private_commit(folder, f"Generated docker-compose-file")
        write_message_to_stderr(f"Not implemented yet")
        return 1

    # </applyconfiguration-command>

    # <run-command>

    def run(self, configurationfile: str):
        if(self.verbose):
            write_message_to_stdout(f"configurationfile: '{configurationfile}'")
        return self._private_execute_task("Run", lambda: self._private_run(configurationfile))

    def _private_run(self, configurationfile: str):
        self._private_save(configurationfile)
        self._private_stop_environment(configurationfile)
        self._private_applyconfiguration(configurationfile)
        self._private_start_environment(configurationfile)
        return 0

    # </run-command>

    # <save-command>

    def save(self, configurationfile: str):
        if(self.verbose):
            write_message_to_stdout(f"configurationfile: '{configurationfile}'")
        return self._private_execute_task("Save", lambda: self._private_save(configurationfile))

    def _private_save(self, configurationfile: str):
        configuration = configparser.ConfigParser()
        configuration.read(configurationfile)
        self._private_commit(configuration.get(self._configuration_section_general, self._configuration_section_general_key_dockercomposefile), f"Saved changes")
        return 0

    # </save-command>

    # <helper-functions>

    def get_dockercompose_file_content(self, configuration: ConfigParser):
        return f"""version: '3'
services:
  {configuration.get(self._configuration_section_general,self._configuration_section_general_key_name)}:
    image: '{configuration.get(self._configuration_section_general,self._configuration_section_general_key_image)}'
    ports:
      TODO:<ports>
    volumes:
      TODO:<volumes>
    container_name: '{configuration.get(self._configuration_section_general,self._configuration_section_general_key_name)}'
"""

    def create_file_in_repository(self, folder, filename, filecontent):
        file = os.path.join(folder, filename)
        write_text_to_file(file, filecontent, self.encoding)
        if(self.verbose):
            write_message_to_stdout(f"Created file '{file}'")

    def get_license_file_content(self, configuration: ConfigParser):
        return f"""Owner of this repository and its content: {configuration.get(self._configuration_section_general,self._configuration_section_general_key_owner)}
Only the owner of this repository is allowed to read, use, change or publish this repository or its content.
"""

    def get_gitignore_file_content(self, configuration: ConfigParser):
        return ""

    def get_readme_file_content(self, configuration: ConfigParser):
        return f"""# Purpose

This repository manages the data of the application '{configuration.get(self._configuration_section_general,self._configuration_section_general_key_name)}'
"""

    def _private_stop_container(self, configuration: ConfigParser):
        execute_and_raise_exception_if_exit_code_is_not_zero("docker-compose", "down", configuration.get(self._configuration_section_general, self._configuration_section_general_key_folder))

    def _private_start_container(self, configuration: ConfigParser):
        execute_and_raise_exception_if_exit_code_is_not_zero("docker-compose", "up -d", configuration.get(self._configuration_section_general, self._configuration_section_general_key_folder))

    def _private_container_is_running(self, configurationfile: str):
        write_message_to_stderr(f"Not implemented yet")
        return False  # TODO

    def _private_commit(self, repository: str, message: str):
        commit_id = git_commit(repository, message, adame_commit_author_name, adame_commit_author_email)
        if(self.verbose):
            write_message_to_stdout(f"Created commit {commit_id} in repository '{repository}'")

    def _private_execute_task(self, name: str, function):
        try:
            if(self.verbose):
                write_message_to_stdout(f"Started task '{name}'")
            return function()
        except Exception as exception:
            exception_message = f"Exception occurred in task '{name}'"
            if(self.verbose):

                write_exception_to_stderr_with_traceback(exception, traceback, exception_message)
            else:
                write_exception_to_stderr(exception, exception_message)
            return 2
        finally:
            if(self.verbose):
                write_message_to_stdout(f"Finished task '{name}'")

    # </helper-functions>

# <commands>


def create_new_environment(name: str, folder: str, image: str, owner: str,  verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.create_new_environment(name, resolve_relative_path_from_current_working_directory(folder), image, owner)


def start_environment(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.start_environment(resolve_relative_path_from_current_working_directory(configuration_file))


def stop_environment(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.stop_environment(configuration_file)


def applyconfiguration(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.applyconfiguration(resolve_relative_path_from_current_working_directory(configuration_file))


def run(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.run(resolve_relative_path_from_current_working_directory(configuration_file))


def save(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    return core.save(resolve_relative_path_from_current_working_directory(configuration_file))

# </commands>

# <miscellaneous>


def get_adame_version():
    return version


def adame_cli():
    arger = argparse.ArgumentParser(description="""Adame
Adame (Automatic Docker Application Management Engine) is a tool which manages (install, start, stop) docker-applications.
One focus of Adame is to store the state of an application: Adame stores all data of the application in git-repositories. So with Adame it is very easy move the application with all its data and configurations to another computer.
Another focus of Adame is it-forensics and it-security: Adame generates a basic snort-configuration for each application to detect/log/bloock networktraffic from the docker-container of the application which is obvious harmful.

Required commandline-commands:
-docker-compose
-git
-snort""", formatter_class=RawTextHelpFormatter)

    arger.add_argument("--verbose", action="store_true")

    subparsers = arger.add_subparsers(dest="command")

    create_command_name = "create"
    create_parser = subparsers.add_parser(create_command_name)
    create_parser.add_argument("name")
    create_parser.add_argument("folder")
    create_parser.add_argument("image")
    create_parser.add_argument("owner")

    start_command_name = "start"
    start_parser = subparsers.add_parser(start_command_name)
    start_parser.add_argument("configurationfile")

    stop_command_name = "stop"
    stop_parser = subparsers.add_parser(stop_command_name)
    stop_parser.add_argument("configurationfile")

    applyconfiguration_command_name = "applyconfiguration"
    applyconfiguration_parser = subparsers.add_parser(applyconfiguration_command_name)
    applyconfiguration_parser.add_argument("configurationfile")

    run_command_name = "run"
    run_parser = subparsers.add_parser(run_command_name)
    run_parser.add_argument("run")

    save_command_name = "save"
    save_parser = subparsers.add_parser(run_command_name)
    save_parser.add_argument("save")

    options = arger.parse_args()
    verbose = options.verbose
    if options.command == create_command_name:
        return create_new_environment(options.name, options.folder, options.image, options.owner, verbose)
    elif options.command == start_command_name:
        return start_environment(options.configurationfile, verbose)
    elif options.command == stop_command_name:
        return stop_environment(options.configurationfile, verbose)
    elif options.command == applyconfiguration_command_name:
        return applyconfiguration(options.configurationfile, verbose)
    elif options.command == run_command_name:
        return run(options.configurationfile, verbose)
    elif options.command == save_command_name:
        return save(options.configurationfile, verbose)
    else:
        if options.command == None:
            write_message_to_stdout(f"Adame {get_adame_version()}")
            write_message_to_stdout(f"Enter a command or run 'adame --help' to get help about the usage")
            return 0
        else:
            write_message_to_stdout(f"Unknown command: {options.command}")
            return 1

# </miscellaneous>
