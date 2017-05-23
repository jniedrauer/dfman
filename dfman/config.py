"""Configuration module"""


import configparser
import os
from pkg_resources import Requirement, resource_filename
import dfman


class Config(configparser.ConfigParser):
    """Create, load, and return configuration"""
    def __init__(self):
        self.default_cfg = resource_filename(Requirement.parse(dfman.NAME), dfman.DEFAULT_CFG)
        self.setup_config()

    def setup_config(self):
        if not os.path.isdir(os.path.dirname(dfman.USER_CFG)):
            os.makedirs(os.path.dirname(dfman.USER_CFG))
        if not os.path.isfile(dfman.USER_CFG):
            self.create_default_user_cfg()

    def create_default_user_cfg(self):
        """Create the stock user config file"""
        with open(self.default_cfg) as default:
            content = default.read()
            with open(dfman.USER_CFG, 'w') as f:
                f.write(content)       
