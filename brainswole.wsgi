import sys
sys.path.insert(0, '/var/www/html/brainswole')

from brainswole import app as application

import logging, sys
logging.basicConfig(stream=sys.stderr)