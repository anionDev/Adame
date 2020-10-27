import pytest
import unittest
from Adame.core import get_adame_version, AdameCore


class MiscellaneousTests(unittest.TestCase):

    def test_adamecore_constructor_does_not_throw_an_exception(self):
        AdameCore()
