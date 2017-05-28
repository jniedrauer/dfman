"""Configuration module"""


import configparser
import os
from dfman import const


class Config(object):
    """Create, load, and return configuration"""
    def __init__(self):
        self.cfg_file = os.path.join(const.USER_PATH, const.CFG)
        self.default_cfg_file = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            const.DEFAULT_PATH,
            const.CFG
        )
        defaults = {
            'verbose': False,
            'backup_format': '%Y-%m-%d-%H-%M-%S',
            'backup_count': '2',
            'dotfile_path': os.path.join(os.environ.get('HOME'), '.dotfiles'),
            'config_path': os.path.join(os.environ.get('HOME'), '.config'),
        }
        self._config = configparser.ConfigParser(defaults)

    def setup_config(self):
        """Initialize configuration files and directories"""
        if not os.path.isfile(self.cfg_file):
            self.create_default_user_cfg()
        self.load_cfg()

    def create_default_user_cfg(self):
        """Create the stock user config file"""
        if not os.path.isdir(const.USER_PATH):
            os.makedirs(const.USER_PATH)
        with open(self.cfg_file, 'w') as f:
            f.write(self.get_default_cfg())

    def get_default_cfg(self):
        """Return the default config file as text"""
        with open(self.default_cfg_file) as f:
            return f.read()

    def load_cfg(self):
        """Load the configuration file"""
        self._config.read(self.cfg_file)

    @property
    def get(self):
        """Return the configuration object"""
        return self._config.get
