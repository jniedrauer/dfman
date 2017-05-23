"""Test CLI module"""


import os
import sys
import unittest
from mock import mock_open, patch
from context import dfman
from dfman import config, const


class TestConfig(unittest.TestCase):

    @patch.object(dfman.config.Config, 'setup_config')
    def test_get_default_cfg_path(self, mock):
        config = dfman.Config()
        self.assertTrue(config.default_cfg.endswith('resources/dfman.conf'))

    @patch('os.makedirs')
    @patch('os.path.isdir')
    @patch('os.path.isfile')
    @patch.object(dfman.config.Config, 'create_default_user_cfg')
    @patch('builtins.open')
    def test_setup_config(self, _, mock_create_default, mock_isfile, mock_isdir, mock_makedirs):
        mock_isdir.return_value = False
        mock_isfile.return_value = False
        config = dfman.Config()

        mock_makedirs.assert_called_once_with(os.path.dirname(const.USER_CFG))
        self.assertTrue(mock_create_default.called)

    @patch('os.makedirs')
    @patch('os.path.isdir')
    @patch('os.path.isfile')
    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_create_default_user_cfg(self, mock_open_, mock_isfile, mock_isdir, mock_makedirs):
        mock_isdir.return_value = False
        mock_isfile.return_value = False
        config = dfman.Config()

        mock_open_.assert_called_with(const.USER_CFG, 'w')
        mock_open_().write.assert_called_with('1')


if __name__ == '__main__':
    unittest.main()
