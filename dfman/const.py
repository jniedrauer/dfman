"""Constants"""


import os


NAME = 'dfman'
CFG = NAME + '.conf'
DEFAULT_PATH = 'resources'
USER_PATH = os.path.join(os.environ.get('HOME'), '.config', NAME)

SYSTEMD_DISTINFO = '/etc/os-release'
