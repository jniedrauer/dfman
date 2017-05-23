"""Core module for dfman"""


import argparse


def main():
    """Read arguments and begin"""
    parser = argparse.ArgumentParser()
    parser.add_argument('operation', choices=['install', 'remove'], help='operation to perform')
    parser.add_argument('--dry-run', help='dry run only', action='store_true')
    args = parser.parse_args()
