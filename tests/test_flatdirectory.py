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

from testsupport import CopyArtifactsTestCase
from beets import config

class CopyArtifactsFromFlatDirectoryTest(CopyArtifactsTestCase):
    """
    Tests to check that copyartifacts copies or moves artifact files from a flat directory.
    i.e. all songs in an album are imported from a single directory
    Also tests extensions config option
    """
    def setUp(self):
        super(CopyArtifactsFromFlatDirectoryTest, self).setUp()

        self._create_flat_import_dir()
        self._setup_import_session(autotag=False)

    def test_only_copy_artifacts_matching_configured_extension(self):
        config['copyartifacts']['extensions'] = '.file'

        self._run_importer()

        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file')
        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')

    def test_copy_all_artifacts_by_default(self):
        self._run_importer()

        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file')
        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')

    def test_copy_artifacts(self):
        self._run_importer()

        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file')
        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')

    def test_ignore_media_files(self):
        self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'track_1.mp3')

    def test_move_artifacts(self):
        config['import']['move'] = True

        self._run_importer()

        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file')
        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')
        self.assert_not_in_import_dir('the_album', 'artifact.file')
        self.assert_not_in_import_dir('the_album', 'artifact.file2')

    def test_prune_import_directory_when_emptied(self):
        """
        Check that plugin does not interfere with normal
        pruning of emptied import directories.
        """
        config['import']['move'] = True

        self._run_importer()

        self.assert_not_in_import_dir('the_album')

    def test_do_nothing_when_not_copying_or_moving(self):
        """
        Check that plugin leaves everthing alone when not
        copying (-C command line option) and not moving.
        """
        config['import']['copy'] = False
        config['import']['move'] = False

        self._run_importer()

        self.assert_number_of_files_in_dir(3, self.import_dir, 'the_album')
        self.assert_in_import_dir('the_album', 'artifact.file')
        self.assert_in_import_dir('the_album', 'artifact.file2')

    def test_rename_when_copying(self):
        config['copyartifacts']['extensions'] = '.file'
        config['paths']['ext:file'] = unicode('$albumpath/$artist - $album')

        self._run_importer()

        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'Tag Artist - Tag Album.file')
        self.assert_in_import_dir('the_album', 'artifact.file')

    def test_rename_when_moving(self):
        config['copyartifacts']['extensions'] = '.file'
        config['paths']['ext:file'] = unicode('$albumpath/$artist - $album')
        config['import']['move'] = True

        self._run_importer()

        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'Tag Artist - Tag Album.file')
        self.assert_not_in_import_dir('the_album', 'artifact.file')


if __name__ == '__main__':
    unittest.main()

