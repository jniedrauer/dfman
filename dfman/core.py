"""Core module for dfman"""


import argparse
import os
from dfman import Config, const


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
        self.verbose = any([self.config.getboolean('Defaults', 'verbose'), self.verbose])

    def get_overrides(self):
        """Get a dict of global and distro overrides"""
        overrides = dict(self.config.items('Overrides'))
        if self.distro:
            overrides.update(self.config.items(self.distro))
        return overrides

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
