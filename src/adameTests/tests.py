from adame import adame
import sys
sys.path.append("..")


def test_1():
    assert adame.get_adame_version() == "0.1.0"


def test_2():
    adame.create_new_environment("name", "repository_folder","image",False)
    assert 1 == 1

