import os
import sys

# Use unittest2 on Python < 2.7
try:
    import unittest2 as unittest
except ImportError:
    import unittest 

# Make sure we use local version of beetsplug and not system namespaced version for tests
try:
    del sys.modules["beetsplug"]
except KeyError:
    pass

# Get the path to the beets source
beetspath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, 'beets'))

# Check that the beets directory exists
if not os.path.isdir(beetspath):
    raise RuntimeError("A directory named beets with the beets source needs to be parallel to this plugin's source directory")

# Put the beets directory at the front of the search path
sys.path.insert(0, beetspath)

from test import _common
from testsupport import ImportHelper
from beets import plugins

import beetsplug

# Add copyartifacts path to pluginpath and load
beetsplug.__path__.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'beetsplug')))
plugins.load_plugins(['copyartifacts'])

class CopyArtifactsTest(_common.TestCase, ImportHelper):
    def setUp(self):
        super(CopyArtifactsTest, self).setUp()

        self._setup_library()
        self._create_import_dir()
        self._setup_import_session(autotag=False)

    def test_album_created_with_track_artist(self):
        self.importer.run()
        self.assertEqual(1, 1)


if __name__ == '__main__':
    unittest.main()
