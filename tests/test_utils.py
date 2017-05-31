"""Test utilities"""


import os
import shutil
import tempfile
from contextlib import contextmanager


@contextmanager
def tempfile_with_content(content):
    tempf = tempfile.NamedTemporaryFile(delete=False, mode='w')
    try:
        tempf.write(content)
        tempf.seek(0)
        yield tempf.name
    finally:
         os.remove(tempf.name)

@contextmanager
def temp_directory():
    tempdir = tempfile.mkdtemp()
    try:
        yield tempdir
    finally:
        shutil.rmtree(tempdir)
