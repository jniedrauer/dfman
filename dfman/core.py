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

    def run_initial_setup(self):
        """Runtime control method"""
        self.config.setup_config()
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
                LOG.warning('%s does not exist - it will be skipped', src)
                continue
            if not self.does_symlink_already_exist(src, dest):
                LOG.debug('Backing up %s to %s', dest, self.config.get('Globals', 'backup_path'))
                if not self.backup_file(dest):
                    # No backup made, skip this file
                    continue
                LOG.debug('Linking %s -> %s', src, dest)
                self.fileop.symlink(src, dest)
            else:
                LOG.debug('%s already linked - skipping', dest)

    def uninstall_dotfiles(self):
        """Reverse install process based on configuration file"""
        if not os.path.isdir(self.config.get('Globals', 'backup_path')):
            raise FileNotFoundError(
                '%s: No such directory' % self.config.get('Globals', 'backup_path')
            )

        for src, dest in self.get_filemap().items():
            if self.does_symlink_already_exist(src, dest):
                LOG.info('removing link for %s', dest)
                self.fileop.unlink(dest)
            else:
                LOG.warning('%s is not linked - skipping', dest)
                continue
            backup = os.path.join(
                self.config.get('Globals', 'backup_path'), os.path.basename(src)
            )
            if os.path.exists(backup):
                self.fileop.move(backup, dest)
                LOG.info('restored %s to %s', backup, src)
            else:
                LOG.warning('backup was not found for %s - not restored', src)

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
            LOG.debug("%s doesn't exist - skipping backup", dest)
            return True
        backup_dest = os.path.join(
            self.config.get('Globals', 'backup_path'),
            os.path.basename(dest)
        )
        if os.path.exists(backup_dest):
            LOG.warning('%s already exists - it will be skipped', backup_dest)
            return False
        self.fileop.move(dest, backup_dest)
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


def main():
    """Read arguments and begin"""
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['install', 'uninstall'], help='operation to perform')
    parser.add_argument('-v', '--verbose', help='print verbosely', action='store_true')
    parser.add_argument('--dry-run', help='dry run only', action='store_true')
    args = parser.parse_args()

    runtime = MainRuntime(args.verbose, args.dry_run)
    runtime.run_initial_setup()

    if args.dry_run:
        LOG.info('Starting dry run')

    if args.operation == 'install':
        runtime.install_dotfiles()
    elif args.operation == 'uninstall':
        runtime.uninstall_dotfiles()

    if args.dry_run:
        LOG.info('Ending dry run')

