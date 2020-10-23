from Adame.core import get_adame_version, AdameCore
import pytest
import unittest


class MiscellaneousTests(unittest.TestCase):

    def test_adamecore_constructor_does_not_throw_an_exception(self):
        AdameCore()
