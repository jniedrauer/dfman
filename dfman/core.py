"""Core module for dfman"""


import argparse
from dfman import Config


class MainRuntime(object):
    """Main runtime class"""
    def __init__(self, verbose, dry_run):
        self.verbose = verbose
        self.dry_run = dry_run
        self.config = Config()

    def run_initial_setup(self):
        """Runtime control method"""
        self.config.setup_config()
        # Set verbose if verbose specified in config or args
        self.verbose = any([self.config.getboolean('Defaults', 'verbose'), self.verbose])


def main():
    """Read arguments and begin"""
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['install', 'remove'], help='operation to perform')
    parser.add_argument('-v', '--verbose', help='print verbosely', action='store_true')
    parser.add_argument('--dry-run', help='dry run only', action='store_true')
    args = parser.parse_args()

    runtime = MainRuntime(args.verbose, args.dry_run)
    runtime.run_initial_setup()
