import os
import sys

from tests.helper import CopyArtifactsTestCase
from beets import config

class CopyArtifactsFromNestedDirectoryTest(CopyArtifactsTestCase):
    """
    Tests to check that copyartifacts copies or moves artifact files from a nested directory
    structure. i.e. songs in an album are imported from two directories corresponding to
    disc numbers or flat option is used
    """
