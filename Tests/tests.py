import pytest
import unittest
from Adame.core import get_adame_version, AdameCore


class MiscellaneousTests(unittest.TestCase):

    def test_adamecore_constructor_does_not_throw_any_exception(self):
        AdameCore()

    def test_command_create(self):
        pass  # TODO implement test

    def test_command_start(self):
        pass  # TODO implement test

    def test_command_stop(self):
        pass  # TODO implement test
