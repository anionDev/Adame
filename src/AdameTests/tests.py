from Adame.core import get_adame_version, create_new_environment, AdameCore
import pytest


def test_adamecore_constructor_does_not_throw_an_exception():
    AdameCore()
