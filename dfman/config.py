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
            'verbose': 'false',
            'backup_path': '~/.dfman/backups',
            'dotfile_path': '~/.dotfiles/files',
            'config_path': '~/.config',
            'log': '~/.dfman/dfman.log',
            'loglevel': 'DEBUG',
        }
        self._config = configparser.ConfigParser(defaults)

    def setup_config(self, init_cfg=None):
        """Initialize configuration files and directories"""
        if not os.path.isfile(self.cfg_file):
            self.create_default_user_cfg(init_cfg=init_cfg)
        elif init_cfg:
            raise FileExistsError('%s: Already exists' % self.cfg_file)
        self.load_cfg()

    def create_default_user_cfg(self, init_cfg=None):
        """Create the stock user config file"""
        cfg = init_cfg or self.default_cfg_file
        if not os.path.isdir(const.USER_PATH):
            os.makedirs(const.USER_PATH)
        with open(self.cfg_file, 'w') as f:
            with open(cfg) as cfg_f:
                f.write(cfg_f.read())

    def load_cfg(self):
        """Load the configuration file"""
        self._config.read(self.cfg_file)

    @property
    def get(self):
        """Return the configuration string"""
        return self._config.get

    @property
    def getboolean(self):
        """Return the configuration boolean"""
        return self._config.getboolean

    @property
    def getint(self):
        """Return the configuration int"""
        return self._config.getint

    def items(self, section):
        """Return all items in a configuration section, excluding defaults"""
        return [i for i in self._config.items(section) if i[0] not in self._config.defaults()]
