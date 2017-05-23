"""Configuration module"""


import configparser
import os
from pkg_resources import Requirement, resource_filename
from dfman import const


class Config(object):
    """Create, load, and return configuration"""
    def __init__(self):
        self.default_cfg = resource_filename(Requirement.parse(const.NAME), const.DEFAULT_CFG)
        self.setup_config()

    def setup_config(self):
        """Initialize configuration files and directories"""
        if not os.path.isdir(os.path.dirname(const.USER_CFG)):
            os.makedirs(os.path.dirname(const.USER_CFG))
        if not os.path.isfile(const.USER_CFG):
            self.create_default_user_cfg()

    def create_default_user_cfg(self):
        """Create the stock user config file"""
        with open(self.default_cfg) as default:
            content = default.read()
            with open(const.USER_CFG, 'w') as f:
                f.write(content)
