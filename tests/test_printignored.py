import os
import sys

# Use unittest2 on Python < 2.7
try:
    import unittest2 as unittest
except ImportError:
    import unittest

# Make sure we use local version of beetsplug and not system namespaced version for tests
#try:
#    del sys.modules["beetsplug"]
#except KeyError:
#    pass

# Get the path to the beets source
beetspath = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'beets'))

# Check that the beets directory exists
if not os.path.isdir(beetspath):
    raise RuntimeError("A directory named beets with the beets source needs to be parallel to this plugin's source directory")

# Put the beets directory at the front of the search path
sys.path.insert(0, beetspath)

from test import helper
from beets import plugins
from beets import config
from testsupport import CopyArtifactsTestCase

from beetsplug import copyartifacts

# Add copyartifacts path to pluginpath and load
#beetsplug.__path__.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'beetsplug')))
#plugins.load_plugins(['copyartifacts'])

class CopyArtifactsPrintIgnoredTest(CopyArtifactsTestCase):
    """
    Tests to check print ignored files functionality and configuration.
    """
    def setUp(self):
        super(CopyArtifactsPrintIgnoredTest, self).setUp()

        self._create_flat_import_dir()
        self._setup_import_session(autotag=False)

    def test_do_not_print_ignored_by_default(self):
        config['copyartifacts']['extensions'] = '.file'

        with helper.capture_log() as logs:
            self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')

        # check output log
        logs = [line for line in logs if line.startswith('copyartifacts:')]
        self.assertEqual(logs, [])

    def test_print_ignored(self):
        config['copyartifacts']['print_ignored'] = True
        config['copyartifacts']['extensions'] = '.file'

        with helper.capture_log() as logs:
            self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')

        # check output log
        logs = [line for line in logs if line.startswith('copyartifacts:')]
        self.assertEqual(logs, [
            'copyartifacts: Ignored files:',
            'copyartifacts:    artifact.file2',
        ])


if __name__ == '__main__':
    unittest.main()

