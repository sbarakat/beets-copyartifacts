import os
import sys

from helper import CopyArtifactsTestCase, capture_log
from beets import config

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

        with capture_log() as logs:
            self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')

        # check output log
        logs = [line for line in logs if line.startswith('copyartifacts:')]
        self.assertEqual(logs, [])

    def test_print_ignored(self):
        config['copyartifacts']['print_ignored'] = True
        config['copyartifacts']['extensions'] = '.file'

        with capture_log() as logs:
            self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')

        # check output log
        logs = [line for line in logs if line.startswith('copyartifacts:')]
        self.assertEqual(logs, [
            'copyartifacts: Ignored files:',
            'copyartifacts:    artifact.file2',
        ])

