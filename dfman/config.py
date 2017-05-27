"""Configuration module"""


import configparser
import os
from pkg_resources import Requirement, resource_filename
from dfman import const


class Config(object):
    """Create, load, and return configuration"""
    def setup_config(self):
        """Initialize configuration files and directories"""
        if not os.path.isdir(os.path.dirname(const.USER_CFG)):
            os.makedirs(os.path.dirname(const.USER_CFG))
        if not os.path.isfile(const.USER_CFG):
            self.create_default_user_cfg()

    def get_default_cfg(self):
        """Return the default config file as text"""
        default_cfg = resource_filename(Requirement.parse(const.NAME), const.DEFAULT_CFG)
        with open(default_cfg) as f:
            return f.read()

    def create_default_user_cfg(self):
        """Create the stock user config file"""
        default_cfg = resource_filename(Requirement.parse(const.NAME), const.DEFAULT_CFG)
        with open(const.USER_CFG, 'w') as f:
            f.write(get_default_cfg())
