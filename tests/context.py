"""Initialize testing environment"""


import logging
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dfman

logging.disable(logging.CRITICAL)
