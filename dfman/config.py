"""Configuration module"""


import configparser
import os
from dfman import const


class Config(object):
    """Create, load, and return configuration"""
    def setup_config(self):
        """Initialize configuration files and directories"""
        if not os.path.isdir(const.USER_PATH):
            os.makedirs(const.USER_PATH)
        if not os.path.isfile(os.path.join(const.USER_PATH, const.CFG)):
            self.create_default_user_cfg()

    def get_default_cfg(self):
        """Return the default config file as text"""
        default_cfg = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            const.DEFAULT_PATH,
            const.CFG
        )
        with open(default_cfg) as f:
            return f.read()

    def create_default_user_cfg(self):
        """Create the stock user config file"""
        with open(os.path.join(const.USER_PATH, const.CFG), 'w') as f:
            f.write(self.get_default_cfg())
