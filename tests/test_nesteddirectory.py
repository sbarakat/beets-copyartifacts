import os
import sys

# Use unittest2 on Python < 2.7
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Get the path to the beets source
beetspath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'beets'))

# Check that the beets directory exists
if not os.path.isdir(beetspath):
    raise RuntimeError("A directory named beets with the beets source needs to be parallel to this plugin's source directory")

# Put the beets directory at the front of the search path
sys.path.insert(0, beetspath)

from helper import CopyArtifactsTestCase
from beets import config

class CopyArtifactsFromNestedDirectoryTest(CopyArtifactsTestCase):
    """
    Tests to check that copyartifacts copies or moves artifact files from a nested directory
    structure. i.e. songs in an album are imported from two directories corresponding to
    disc numbers or flat option is used
    """

if __name__ == '__main__':
    unittest.main()

