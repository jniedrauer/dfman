"""Test CLI module"""


import unittest
from mock import ANY, call, MagicMock, Mock, patch
from context import dfman


class TestCLI(unittest.TestCase):

    def test_dummy(self):
        cli = dfman.CLI()
        self.assertEqual(cli.dummy, True)


if __name__ == '__main__':
    unittest.main()
