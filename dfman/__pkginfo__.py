# pylint: disable=invalid-name,redefined-builtin
"""dfman package info"""


import os


modname = distname = 'dfman'
numversion = (0, 0, 2)
version = '.'.join([str(num) for num in numversion])

install_requires = [
]

license = 'MIT'
description = 'Dotfile Manager'
url = 'https://github.com/jniedrauer/dfman'
author = 'Josiah Niedrauer'
author_email = 'jniedrauer@gmail.com'

classifiers = [
    'Development Status :: 2 - Pre-Alpha',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'License :: OSI Approved :: MIT License',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3 :: Only',
    'Topic :: Utilities'
]


long_description = """"""

scripts = [os.path.join('bin', distname)]
