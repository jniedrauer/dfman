"""Core module for dfman"""


import argparse
import logging
import os
import shutil
from configparser import NoSectionError
from datetime import datetime
from dfman import Config, const


LOG = logging.getLogger(__name__)


class MainRuntime(object):
    """Main runtime class"""
    def __init__(self, verbose, dry_run):
        self.verbose = verbose
        self.dry_run = dry_run
        self.config = Config()
        self.distro = self.get_distro()
        self.fileop = FileOperator(self.dry_run)

    def run_initial_setup(self, init_cfg=None):
        """Runtime control method"""
        self.config.setup_config(init_cfg=init_cfg)
        # Set verbose if verbose specified in config or args
        self.verbose = any([
            self.config.getboolean('Globals', 'verbose'),
            self.verbose,
            self.dry_run
        ])
        self.create_runtime_directories()
        self.set_output_streams()

    def create_runtime_directories(self):
        """Create directory tree for backups and logs"""
        for path in (
                os.path.dirname(self.config.get('Globals', 'log')),
                self.config.get('Globals', 'backup_path')
        ):
            if not os.path.isdir(path):
                os.makedirs(path)

    def set_output_streams(self):
        """Set the output streams with logging"""
        if len(LOG.handlers) >= 2: # console and logfile
            return
        LOG.setLevel(logging.DEBUG) # This only sets the minimum logging level
        log_format = logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
        file_out = logging.FileHandler(self.config.get('Globals', 'log'))
        file_out.setFormatter(log_format)
        file_out.setLevel(self.config.get('Globals', 'loglevel'))
        LOG.addHandler(file_out)

        console_out = logging.StreamHandler()
        console_out.setFormatter(logging.Formatter('%(message)s'))
        if self.verbose:
            console_out.setLevel(logging.DEBUG)
        else:
            console_out.setLevel(logging.INFO)
        LOG.addHandler(console_out)

    def install_dotfiles(self):
        # pylint: disable=no-value-for-parameter
        """Install dotfiles based on defaults and overrides"""
        if not os.path.isdir(self.config.get('Globals', 'dotfile_path')):
            raise FileNotFoundError(
                '%s: No such directory' % self.config.get('Globals', 'dotfile_path')
            )

        for src, dest in self.get_filemap().items():
            if not os.path.exists(src):
                LOG.warning('Skipped: %s does not exist', src)
                continue
            if not self.does_symlink_already_exist(src, dest):
                if not self.backup_file(dest):
                    # No backup made, skip this file
                    continue
                self.fileop.symlink(src, dest)
                LOG.debug('Linked: %s to %s', src, dest)
            else:
                LOG.debug('Skipped: %s already linked', dest)

    def uninstall_dotfiles(self):
        """Reverse install process based on configuration file"""
        if not os.path.isdir(self.config.get('Globals', 'backup_path')):
            raise FileNotFoundError(
                '%s: No such directory' % self.config.get('Globals', 'backup_path')
            )

        for src, dest in self.get_filemap().items():
            if self.does_symlink_already_exist(src, dest):
                self.fileop.unlink(dest)
                LOG.debug('Unlinked: %s', dest)
            else:
                LOG.debug('Skipped: %s is not linked', dest)
                continue
            backup = os.path.join(
                self.config.get('Globals', 'backup_path'), os.path.basename(src)
            )
            if os.path.exists(backup):
                self.fileop.move(backup, dest)
                LOG.debug('Restored: %s to %s', backup, src)
            else:
                LOG.error('Not restored: %s not found in backups', backup)

    def add_file(self, existing_file):
        """Add a file to tracking"""
        if existing_file.endswith(os.sep):
            existing_file = existing_file.rstrip(os.sep)
        path, basename = os.path.split(existing_file)
        if path == os.environ.get('HOME'):
            path = '~'
        dest = os.path.join(self.config.get('Globals', 'dotfile_path'), basename)
        if not os.path.exists(existing_file):
            raise FileNotFoundError('%s: No such file or directory' % existing_file)
        if os.path.exists(dest):
            raise FileExistsError('%s: Already exists' % dest)
        if not path == self.config.get('Globals', 'config_path'):
            self.add_file_to_overrides(os.path.join(path, basename))

        self.fileop.move(existing_file, dest)
        LOG.debug('Added: %s', existing_file)

    def add_file_to_overrides(self, filepath):
        """Add a file to overrides section of config file"""
        filename = os.path.basename(filepath)
        with open(os.path.join(const.USER_PATH, const.CFG)) as f:
            content = f.readlines()
        line = content.index('[Overrides]' + os.linesep) + 1
        content.insert(line, '%s = %s%s' % (filename, filepath, os.linesep))
        self.fileop.writelines(os.path.join(const.USER_PATH, const.CFG), 'w', content)

    def get_filemap(self):
        """Return a map of all file sources and destinations with overrides"""
        filemap = {
            os.path.join(self.config.get('Globals', 'dotfile_path'), i):
                os.path.join(self.config.get('Globals', 'config_path'), i)
            for i in os.listdir(self.config.get('Globals', 'dotfile_path'))
        }
        overrides = self.get_overrides()
        filemap.update(overrides)
        return filemap

    def get_overrides(self):
        """Get a dict of global and distro overrides"""
        overrides = dict(self.config.items('Overrides'))
        if self.distro:
            try:
                overrides.update(self.config.items(self.distro))
            except NoSectionError:
                pass
        return {
            os.path.join(self.config.get('Globals', 'dotfile_path'), key): value
            for key, value in overrides.items()
        }

    def backup_file(self, dest):
        """Back up dest to backup dir if it isn't already
        a symlink to src"""
        if not os.path.exists(dest):
            LOG.debug("Not backed up: %s doesn't exist", dest)
            return True
        backup_dest = os.path.join(
            self.config.get('Globals', 'backup_path'),
            os.path.basename(dest)
        )
        if os.path.exists(backup_dest):
            LOG.error('Skipped: %s already exists in backups', backup_dest)
            return False
        self.fileop.move(dest, backup_dest)
        LOG.debug('Backed up: %s to %s', dest, self.config.get('Globals', 'backup_path'))
        return True

    @staticmethod
    def does_symlink_already_exist(src, dest):
        """Return True if a symlink already exists for dest->src or False"""
        return os.path.realpath(dest) == src

    @staticmethod
    def get_distro():
        """Return the distro ID"""
        if not os.path.isfile(const.SYSTEMD_DISTINFO):
            return None
        with open(const.SYSTEMD_DISTINFO) as f:
            for line in f:
                if line.startswith('ID='):
                    return line.rstrip().split('ID=')[-1]
        return None


class FileOperator(object):
    # pylint: disable=no-self-argument,missing-docstring,not-callable,no-self-use
    """Dry-run aware file operations"""
    def __init__(self, dry_run):
        self.dry_run = dry_run

    def _not_dry_run(func):
        def conditional(*args):
            if not args[0].dry_run:
                return func(*args)
        return conditional

    @_not_dry_run
    def move(self, *args):
        shutil.move(*args)

    @_not_dry_run
    def makedirs(self, *args):
        os.makedirs(*args)

    @_not_dry_run
    def symlink(self, *args):
        os.symlink(*args)

    @_not_dry_run
    def unlink(self, *args):
        os.unlink(*args)

    @_not_dry_run
    def writelines(self, dest, mode, content):
        with open(dest, mode) as f:
            f.writelines(content)


def main():
    """Read arguments and begin"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'operation', choices=['install', 'uninstall'], help='operation to perform'
    )
    parser.add_argument('-i', '--init', required=False, help='provide initial configuration file')
    parser.add_argument('-a', '--add', required=False, help='add a dotfile')
    parser.add_argument('-v', '--verbose', help='print verbosely', action='store_true')
    parser.add_argument('--dry-run', help='dry run only', action='store_true')
    args = parser.parse_args()

    runtime = MainRuntime(args.verbose, args.dry_run)
    runtime.run_initial_setup(init_cfg=args.init)

    if args.dry_run:
        LOG.info('STARTING DRY RUN')

    if args.operation == 'install':
        if args.add:
            runtime.add_file(args.add)
            runtime.run_initial_setup() # Re-load config
        runtime.install_dotfiles()
    elif args.operation == 'uninstall':
        if args.init:
            parser.error('--init should not be used with uninstall')
        if args.add:
            parser.error('--add should not be used with uninstall')
        runtime.uninstall_dotfiles()

    if args.dry_run:
        LOG.info('ENDING DRY RUN')
