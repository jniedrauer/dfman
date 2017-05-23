"""Constants"""


import os


NAME = 'dfman'
DEFAULT_CFG = os.path.join('resources', NAME + '.conf')
USER_CFG = os.path.join(os.environ.get('HOME'), NAME, NAME + '.conf')
