import os
import sys

# Use unittest2 on Python < 2.7
try:
    import unittest2 as unittest
except ImportError:
    import unittest

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

