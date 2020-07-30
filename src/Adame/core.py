import argparse
from argparse import RawTextHelpFormatter
from ScriptCollection.core import write_message_to_stdout, write_message_to_stderr, write_exception_to_stderr_with_traceback, write_exception_to_stderr
import sys
import traceback
version = "0.2.2"


class AdameCore(object):
    verbose = False

    def __init__(self):
        pass

    def create_new_environment(self, name: str, folder: str, image: str):
        return self._private_execute_task("Create new environment", lambda: self._private_create_new_environment(name, folder, image))

    def _private_create_new_environment(self, name: str, folder: str, image: str):
        write_message_to_stdout(f"name: {name}")
        write_message_to_stdout(f"folder: {folder}")
        write_message_to_stdout(f"image: {image}")
        write_message_to_stderr("This function is not implemented yet.")
        return 1

    def start_environment(self, configuration_file: str):
        return self._private_execute_task("Start environment", lambda: self._private_start_environment(configuration_file))

    def _private_start_environment(self, configurationfile: str):
        write_message_to_stdout(f"configurationfile: {configurationfile}")
        write_message_to_stderr("This function is not implemented yet.")
        return 1

    def stop_environment(self, configurationfile: str):
        return self._private_execute_task("Stop environment", lambda: self._private_stop_environment(configurationfile))

    def _private_stop_environment(self, configurationfile: str):
        write_message_to_stdout(f"configurationfile: {configurationfile}")
        write_message_to_stderr("This function is not implemented yet.")
        return 1

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


def create_new_environment(name: str, folder: str, image: str, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    core.create_new_environment(name, folder, image)


def start_environment(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    core.start_environment(configuration_file)


def stop_environment(configuration_file, verbose: bool):
    core = AdameCore()
    core.verbose = verbose
    core.stop_environment(configuration_file)


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

    start_command_name = "start"
    start_parser = subparsers.add_parser(start_command_name)
    start_parser.add_argument("configurationfile")

    stop_command_name = "stop"
    stop_parser = subparsers.add_parser(stop_command_name)
    stop_parser.add_argument("configurationfile")

    options = arger.parse_args()
    verbose = options.verbose
    if options.command == create_command_name:
        return create_new_environment(options.name, options.folder, options.image, verbose)
    elif options.command == start_command_name:
        return start_environment(options.configurationfile, verbose)
    elif options.command == stop_command_name:
        return stop_environment(options.configurationfile, verbose)
    else:
        if options.command == None:
            write_message_to_stdout(f"Adame {get_adame_version()}")
            write_message_to_stdout(f"Enter a command or run 'adame --help' to get help about the usage")
            return 0
        else:
            write_message_to_stdout(f"Unknown command: {options.command}")
            return 1
