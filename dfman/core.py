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

    def run_initial_setup(self):
        """Runtime control method"""
        self.config.setup_config()
        # Set verbose if verbose specified in config or args
        self.verbose = any([self.config.getboolean('Globals', 'verbose'), self.verbose])
        self.create_runtime_directories()
        self.set_output_streams()

    def create_runtime_directories(self):
        """Create directory tree for backups and logs"""
        for path in (
                os.path.dirname(self.config.get('Globals', 'log')),
                self.config.get('Backups', 'backup_path')
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

        if self.verbose:
            console_out = logging.StreamHandler()
            console_out.setLevel(logging.INFO)
            console_out.setFormatter(logging.Formatter('%(message)s'))
            LOG.addHandler(console_out)

    def install_dotfiles(self):
        # pylint: disable=no-value-for-parameter
        """Install dotfiles based on defaults and overrides"""
        if not os.path.isdir(self.config.get('Globals', 'dotfile_path')):
            raise OSError('%s: No such directory' % self.config.get('Globals', 'dotfile_path'))

        LOG.info(
            'Installing contents of %s to %s',
            self.config.get('Globals', 'config_path'),
            self.config.get('Globals', 'dotfile_path')
        )

        filemap = self.get_filemap()
        for src, dest in filemap.items():
            if not os.path.exists(src):
                LOG.warning('%s does not exist - it will be skipped', src)
                continue
            if not self.does_symlink_already_exist(src, dest):
                LOG.info('Backing up %s to %s', dest, self.config.get('Backups', 'backup_path'))
                if not self.backup_file(dest):
                    # No backup made, skip this file
                    continue
            LOG.info('Linked %s->%s', src, dest)
            self.create_link(src, dest)

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
            LOG.info("%s doesn't exist, skipping", dest)
            return True
        timestamp = datetime.now().strftime(self.config.get('Backups', 'backup_format'))
        backup_dest = os.path.join(
            self.config.get('Backups', 'backup_path'),
            '-'.join([os.path.basename(dest), timestamp])
        )
        if os.path.exists(backup_dest):
            LOG.warning('%s already exists - it will be skipped', backup_dest)
            return False
        shutil.move(dest, backup_dest)
        return True

    @staticmethod
    def create_link(src, dest):
        """Create a symlink of src->dest"""
        os.symlink(src, dest)

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


def main():
    """Read arguments and begin"""
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['install', 'remove'], help='operation to perform')
    parser.add_argument('-v', '--verbose', help='print verbosely', action='store_true')
    parser.add_argument('--dry-run', help='dry run only', action='store_true')
    args = parser.parse_args()

    runtime = MainRuntime(args.verbose, args.dry_run)
    runtime.run_initial_setup()

    if args.operation == 'install':
        runtime.install_dotfiles()
