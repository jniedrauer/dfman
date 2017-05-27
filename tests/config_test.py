"""Test CLI module"""


import os
import sys
import unittest
from mock import mock_open, patch
from context import dfman
from dfman import config, const


class TestConfig(unittest.TestCase):

    @patch('os.makedirs')
    @patch('os.path.isdir')
    @patch('os.path.isfile')
    @patch.object(dfman.config.Config, 'create_default_user_cfg')
    def test_setup_config(self, mock_create_default, mock_isfile, mock_isdir, mock_makedirs):
        mock_isdir.return_value = False
        mock_isfile.return_value = False
        config = dfman.Config()
        config.setup_config()

        mock_makedirs.assert_called_once_with(os.path.dirname(const.USER_CFG))
        self.assertTrue(mock_create_default.called)

    def test_get_default_cfg(self):
        config = dfman.Config()
        res = config.get_default_cfg()
        self.assertTrue(isinstance(res, basestring))


    @patch.object(dfman.config.Config, 'get_default_cfg')
    @patch('builtins.open', new_callable=mock_open, read_data='1')
    def test_create_default_user_cfg(self, mock_get_default_cfg, mock_open_obj):
        expected_value = 'a_string'
        mock_get_default_cfg.return_value = expected_value
        config = dfman.Config()
        config.create_default_user_cfg()

        mock_open_obj.assert_called_with(const.USER_CFG, 'w')
        mock_open_obj().write.assert_called_with(expected_value)


if __name__ == '__main__':
    unittest.main()
