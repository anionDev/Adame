from Adame.core import get_adame_version, create_new_environment, AdameCore
import pytest
import unittest


class MiscellaneousTests(unittest.TestCase):

    def test_adamecore_constructor_does_not_throw_an_exception(self):
        AdameCore()
