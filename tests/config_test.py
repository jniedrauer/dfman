"""Test config module"""


import os
import tempfile
import unittest
from mock import call, mock_open, patch
import test_utils
from context import dfman
from dfman import config, const


class TestConfig(unittest.TestCase):

    @patch('dfman.config.os.path.isdir')
    @patch('dfman.config.os.makedirs')
    @patch('builtins.open', new_callable=mock_open, read_data='a_string')
    def test_create_default_user_cfg(self, mock_open_obj, mock_isdir, mock_makedirs):
        mock_isdir.return_value = False

        config_ = dfman.Config()
        config_.create_default_user_cfg()

        mock_makedirs.assert_called_once_with(const.USER_PATH)

        calls = [
            call(os.path.join(const.USER_PATH, const.CFG), 'w'),
            call(config_.default_cfg_file)
        ]
        mock_open_obj.assert_has_calls(calls, any_order=True)
        mock_open_obj().write.assert_called_once_with('a_string')

    @patch('dfman.config.os.makedirs')
    def test_get_config_value(self, _):
        config_ = dfman.Config()
        test_config = \
'''
[Test]
testvalue = 123
config_path = ~/.config
'''
        with test_utils.tempfile_with_content(test_config) as tmp:
            config_.cfg_file = tmp
            config_.load_cfg()

            self.assertEqual(config_.get('Test', 'testvalue'), '123')
            self.assertEqual(
                config_.getpath('Test', 'config_path'),
                os.path.join(os.environ.get('HOME'),'.config')
            )

    def test_items(self):
        config_ = dfman.Config()
        expected_items = {'testvalue': '123'}
        test_config = \
'''
[Test]
testvalue = 123
'''
        with test_utils.tempfile_with_content(test_config) as tmp:
            config_.cfg_file = tmp
            config_.load_cfg()

            result = config_.items('Test')

            self.assertEqual(dict(result), expected_items)


if __name__ == '__main__':
    unittest.main()
