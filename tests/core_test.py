"""Test core module"""


import os
import sys
import unittest
from contextlib import contextmanager
from mock import call, mock_open, patch
import test_utils
from context import dfman
from dfman import config, const, core


class TestMainRuntime(unittest.TestCase):

    @patch('dfman.core.Config')
    @patch.object(dfman.core.MainRuntime, 'set_output_streams')
    @patch.object(dfman.core.MainRuntime, 'create_runtime_directories')
    def test_run_initial_setup(self, _1, _2, mock_config):
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

        # dry run is set to true with args, verbose is false
        mc_return.getboolean.return_value = False
        runtime = dfman.core.MainRuntime(False, True)
        runtime.run_initial_setup()

    def test_get_distro(self):
        test_os = \
'''
NAME="Scary Linux"
ID=spooky
PRETTY_NAME="Spooky Scary Linux"
ANSI_COLOR="1;32"
'''
        with test_utils.tempfile_with_content(test_os) as tmp:
            runtime = dfman.core.MainRuntime(False, False)
            const.SYSTEMD_DISTINFO = tmp
            self.assertEqual(runtime.get_distro(), 'spooky')

    def test_get_overrides(self):
        test_config = \
'''
[Globals]
dotfile_path = srcdir

[Overrides]
file1 = dir1/file1
file2 = dir2/file2

[spooky]
file2 = distoverride/file2
'''
        with test_utils.tempfile_with_content(test_config) as tmp:
            config = dfman.Config()
            config.cfg_file = tmp
            config.load_cfg()

        runtime = dfman.core.MainRuntime(False, False)
        runtime.config = config
        runtime.distro = 'spooky'
        overrides = runtime.get_overrides()
        self.assertEqual(overrides[os.path.join('srcdir', 'file1')], 'dir1/file1')
        self.assertEqual(overrides[os.path.join('srcdir', 'file2')], 'distoverride/file2')

    @patch('dfman.core.os')
    @patch('dfman.core.Config')
    def test_create_runtime_directories(self, mock_config, mock_os):
        mc = mock_config.return_value
        mc.get.return_value = 'backup_path'
        mock_os.path.dirname.return_value = 'logpath'
        mock_os.path.isdir.return_value = False

        runtime = dfman.core.MainRuntime(False, False)
        runtime.create_runtime_directories()

        calls = [call('backup_path'), call('logpath')]
        mock_os.makedirs.assert_has_calls(calls, any_order=True)

    @patch('dfman.core.os.listdir')
    @patch('dfman.core.Config')
    @patch.object(dfman.core.MainRuntime, 'get_overrides')
    def test_get_filemap(self, mock_overrides, mock_config, mock_listdir):
        mc = mock_config.return_value
        mc.get.return_value = 'test_path'
        mock_listdir.return_value = ['1', '2']
        overrides = {os.path.join('test_path', '1'): os.path.join('test_path', '3')}
        mock_overrides.return_value = overrides
        expected = {
            os.path.join('test_path', '1'): os.path.join('test_path', '3'),
            os.path.join('test_path', '2'): os.path.join('test_path', '2')
        }

        runtime = dfman.core.MainRuntime(False, False)
        result = runtime.get_filemap()

        self.assertEqual(result, expected)

    @patch('dfman.core.os.path.exists')
    @patch('dfman.core.Config')
    @patch('dfman.core.shutil')
    def test_backup_file(self, mock_shutil, mock_config, mock_exists):
        mc = mock_config.return_value
        mc.get.return_value = 'backup_path'
        src = 'src'
        dest = 'dest'
        # File to back up doesn't exist so it should return success
        mock_exists.return_value = False

        runtime = dfman.core.MainRuntime(False, False)
        result = runtime.backup_file(dest)

        mock_exists.assert_called_once_with('dest')
        self.assertTrue(result)

        # File exists in src and dest so it should fail
        mock_exists.reset_mock()
        mock_exists.return_value = True
        calls = [call('dest'), call(os.path.join('backup_path', 'dest'))]

        result = runtime.backup_file(dest)

        mock_exists.assert_has_calls(calls)
        self.assertFalse(result)

        # File exists in src but not in dest so it should actually make a backup
        mock_exists.reset_mock()
        mock_exists.side_effect = [True, False]

        result = runtime.backup_file(dest)

        mock_shutil.move.assert_called_once_with(
            'dest', os.path.join('backup_path', 'dest')
        )
        self.assertTrue(result)

    def test_does_symlink_already_exist(self):
        src = 'src'
        dest = 'dest'
        with test_utils.temp_directory() as tmpdir:
            srcpath = os.path.join(tmpdir, src)
            destpath = os.path.join(tmpdir, dest)
            open(srcpath, 'a').close()
            os.symlink(srcpath, destpath)

            runtime = dfman.core.MainRuntime(False, False)

            # symlink already exists
            result = runtime.does_symlink_already_exist(srcpath, destpath)

            self.assertTrue(result)

            # symlink doesn't exist
            os.remove(destpath)

            result = runtime.does_symlink_already_exist(srcpath, destpath)

            self.assertFalse(result)

    @patch('dfman.core.os')
    @patch('dfman.core.Config')
    @patch.object(dfman.core.FileOperator, 'move')
    @patch.object(dfman.core.FileOperator, 'unlink')
    @patch.object(dfman.core.MainRuntime, 'get_filemap')
    @patch.object(dfman.core.MainRuntime, 'does_symlink_already_exist')
    def test_uninstall_dotfiles(
            self, mock_test_symlink, mock_get_filemap, mock_unlink, mock_move, mock_config, mock_os
    ):
        mc = mock_config.return_value
        mc.get.return_value = 'backup_path'

        mock_get_filemap.return_value = {'dotfile_path/src': 'config_path/file'}
        mock_os.path.isfile.return_value = False

        # missing backup path
        mock_os.path.isdir.return_value = False

        runtime = dfman.core.MainRuntime(False, False)

        with self.assertRaises(OSError):
            runtime.uninstall_dotfiles()

        # symlink not installed
        mock_os.path.isdir.return_value = True
        mock_test_symlink.return_value = False

        runtime.uninstall_dotfiles()

        mock_unlink.assert_not_called()

        # symlink and backup exist
        mock_os.path.exists.return_value = True
        mock_test_symlink.return_value = True
        mock_os.path.join.return_value = 'backup_path/file'

        runtime.uninstall_dotfiles()

        mock_unlink.assert_called_once_with('config_path/file')
        mock_move.assert_called_once_with('backup_path/file', 'config_path/file')


class TestFileOperator(unittest.TestCase):

    @patch('dfman.core.shutil')
    def test_move(self, mock_shutil):
        dry_run = True
        fileop = dfman.core.FileOperator(dry_run)
        fileop.move('src', 'dest')

        mock_shutil.move.assert_not_called()

        dry_run = False
        fileop = dfman.core.FileOperator(dry_run)
        fileop.move('src', 'dest')

        mock_shutil.move.assert_called_once_with('src', 'dest')


if __name__ == '__main__':
    unittest.main()
