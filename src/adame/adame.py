import argparse


class AdameCore(object):
    def __init__(self):
        pass

    def create_new_environment(self, name: str, repository_folder: str):
        return "Hello from Adame: create_new_environment. This function is not implemented yet."

    def start_environment(self, configuration_file: str):
        return "Hello from Adame: stop_environment. This function is not implemented yet. file: "+configuration_file

    def stop_environment(self, configuration_file: str):
        return "Hello from Adame: stop_environment. This function is not implemented yet. file: "+configuration_file

    def test(self):
        return "adame core test"


def create_new_environment(name: str, repository_folder: str):
    AdameCore().create_new_environment(name, repository_folder)


def start_environment(configuration_file):
    AdameCore().start_environment(configuration_file)


def stop_environment(configuration_file):
    AdameCore().stop_environment(configuration_file)


def get_new_adame_core():
    return AdameCore()


def get_adame_version():
    return "0.0.15"


def install_dependencies():
    #make the commands dotnet, docker, git available


def adame_cli():
    print("adame_main "+get_adame_version())
    parser = argparse.ArgumentParser(
        description='Process some integers.', usage="todo")
    parser.add_argument('create', help='Creates a new configuration')
    args = parser.parse_args()
    print("createarg: "+args.create)
    core = AdameCore()
    print(core.test())


if __name__ == '__main__':
    adame_cli()
