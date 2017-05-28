"""Test CLI module"""


import os
import tempfile
import unittest
from mock import mock_open, patch
from context import dfman
from dfman import config, const


class TestConfig(unittest.TestCase):

    @patch('dfman.config.os.path.isdir')
    @patch('dfman.config.os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    @patch.object(dfman.Config, 'get_default_cfg')
    def test_create_default_user_cfg(self, mock_get_default_cfg, mock_open_obj, mock_isdir, mock_makedirs):
        expected_write = 'a_string'
        mock_get_default_cfg.return_value = expected_write
        mock_isdir.return_value = False

        config_ = dfman.Config()
        config_.create_default_user_cfg()

        mock_makedirs.assert_called_once_with(const.USER_PATH)

        mock_open_obj.assert_called_once_with(os.path.join(const.USER_PATH, const.CFG), 'w')
        mock_open_obj().write.assert_called_once_with(expected_write)

    def test_get_default_cfg(self):
        config_ = dfman.Config()
        res = config_.get_default_cfg()

        self.assertIsInstance(res, str)

    @patch('dfman.config.os.makedirs')
    def test_get_config_value(self, _):
        config_ = dfman.Config()
        test_config = \
b'''
[Test]
testvalue = 123
user_home = /test123
config_path = %(user_home)s/.config
'''
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(test_config)
            tmp.seek(0)
            config_.cfg_file = tmp.name
            config_.load_cfg()

            self.assertEqual(config_.get('Test', 'testvalue'), '123')
            self.assertEqual(config_.get('Test', 'config_path'), '/test123/.config')


if __name__ == '__main__':
    unittest.main()
