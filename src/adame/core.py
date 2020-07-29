import argparse
from argparse import RawTextHelpFormatter
import sys
version = "0.1.0"


class AdameCore(object):
    verbose = False

    def __init__(self):
        pass

    def create_new_environment(self, name: str, folder: str, image: str):
        print("Hello from Adame: create_new_environment. This function is not implemented yet. name: "+name+",  folder: "+folder+",  image: "+image)

    def start_environment(self, configuration_file: str):
        print("Hello from Adame: stop_environment. This function is not implemented yet. file: "+configuration_file)

    def stop_environment(self, configuration_file: str):
        print("Hello from Adame: stop_environment. This function is not implemented yet. file: "+configuration_file)


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
One focus of adame is to store the state of an application: Adame stores all data of the application in git-repositories. So with adame it is very easy move the application with all its data and configurations to another computer.
Another focus of adame is it-forensics and it-security: Adame generates a basic snort-configuration for each application to detect/log/bloock networktraffic from the docker-container of the application which is obvious harmful.

Requirements:
-docker
-git
-snort""", formatter_class=RawTextHelpFormatter)

    arger.add_argument("-v", action="store_true")

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
    verbose = options.v
    if options.command == create_command_name:
        create_new_environment(options.name, options.folder, options.image, verbose)
    elif options.command == start_command_name:
        start_environment(options.configurationfile, verbose)
    elif options.command == stop_command_name:
        stop_environment(options.configurationfile, verbose)
    else:
        if options.command == None:
            print("Adame " + get_adame_version())
            print('Enter a command or run "adame --help" to get help about the usage')
        else:
            print("Unknown command: "+options.command)
            sys.exit(1)
    sys.exit(0)
