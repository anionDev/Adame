from adame import adame
import sys
sys.path.append("..")


def test_1():
    assert adame.get_adame_version() == "0.0.15"


def test_2():
    adame.create_new_environment("name", "repository_folder")
    assert 1 == 1


def test_3():
    adame.get_new_adame_core().test()
    assert 1 == 1
