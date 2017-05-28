"""Test CLI module"""


import os
import sys
import tempfile
import unittest
from mock import mock_open, patch
from context import dfman
from dfman import config, const, core


class TestMainRuntime(unittest.TestCase):

    @patch('dfman.core.Config')
    @patch.object(dfman.core.MainRuntime, 'set_output_streams')
    def test_run_initial_setup(self, _, mock_config):
        mc_return = mock_config.return_value
        # dry run and verbose are set to false with args
        mc_return.getboolean.return_value = False
        runtime = dfman.core.MainRuntime(False, False)
        runtime.run_initial_setup()

        self.assertFalse(runtime.dry_run)
        self.assertFalse(runtime.verbose)

        # verbose is set to true with config file but not with args
        mc_return.getboolean.return_value = True
        runtime.run_initial_setup()

        self.assertTrue(runtime.verbose)

    def test_get_distro(self):
        test_os = \
b'''
NAME="Scary Linux"
ID=spooky
PRETTY_NAME="Spooky Scary Linux"
ANSI_COLOR="1;32"
'''
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(test_os)
            tmp.seek(0)

            runtime = dfman.core.MainRuntime(False, False)
            const.SYSTEMD_DISTINFO = tmp.name
            self.assertEqual(runtime.get_distro(), 'spooky')

    def test_get_overrides(self):
        test_config = \
b'''
[Overrides]
file1 = dir1/file1
file2 = dir2/file2

[spooky]
file2 = distoverride/file2
'''
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(test_config)
            tmp.seek(0)
            config = dfman.Config()
            config.cfg_file = tmp.name
            config.load_cfg()

        runtime = dfman.core.MainRuntime(False, False)
        runtime.config = config
        runtime.distro = 'spooky'
        overrides = runtime.get_overrides()

        self.assertEqual(overrides['file1'], 'dir1/file1')
        self.assertEqual(overrides['file2'], 'distoverride/file2')




if __name__ == '__main__':
    unittest.main()
