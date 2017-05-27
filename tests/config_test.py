"""Test CLI module"""


import os
import sys
import unittest
from mock import mock_open, patch
from context import dfman
from dfman import config, const


class TestConfig(unittest.TestCase):

    @patch('dfman.config.os')
    @patch.object(dfman.Config, 'create_default_user_cfg')
    def test_setup_config(self, mock_create_default, mock_os):
        mock_os.path.isdir.return_value = False
        mock_os.path.isfile.return_value = False
        config = dfman.Config()
        config.setup_config()

        mock_os.makedirs.assert_called_once_with(const.USER_PATH)
        self.assertTrue(mock_create_default.called)

    def test_get_default_cfg(self):
        config = dfman.Config()
        res = config.get_default_cfg()

        self.assertIsInstance(res, str)

    @patch('builtins.open', new_callable=mock_open)
    @patch.object(dfman.Config, 'get_default_cfg')
    def test_create_default_user_cfg(self, mock_get_default_cfg, mock_open_obj):
        expected_write = 'a_string'
        mock_get_default_cfg.return_value = expected_write
        config = dfman.Config()
        config.create_default_user_cfg()

        mock_open_obj.assert_called_once_with(os.path.join(const.USER_PATH, const.CFG), 'w')
        mock_open_obj().write.assert_called_once_with(expected_write)


if __name__ == '__main__':
    unittest.main()
