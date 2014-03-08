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

from testsupport import CopyArtifactsTestCase
from beets import plugins
from beets import config

import beetsplug

# Add copyartifacts path to pluginpath and load
beetsplug.__path__.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'beetsplug')))
plugins.load_plugins(['copyartifacts'])

class CopyArtifactsReimportTest(CopyArtifactsTestCase):
    """
    Tests to check that copyartifacts handles reimports correctly
    """
    def setUp(self):
        super(CopyArtifactsReimportTest, self).setUp()
        
        self._create_flat_import_dir()
        self._setup_import_session(autotag=False)

        config['copyartifacts']['extensions'] = '.file'
        
        # Initial import
        self._run_importer()
   
        # Change the path formats so the files in the library are relocated when reimported
        self.original_path_formats = list(self.lib.path_formats)
        self.lib.path_formats[0] = ('default', os.path.join('1$artist', '$album', '$title'))
        
        self._setup_import_session(autotag=False, import_dir=self.lib_dir)

    def test_move_artifacts_with_copy_import(self):
        self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file')
        self.assert_in_lib_dir('1Tag Artist', 'Tag Album', 'artifact.file')

    def test_prune_empty_directories_with_copy_import(self):
        self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist')

    def test_move_artifacts_with_move_import(self):
        config['import']['move'] = True

        self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file')
        self.assert_in_lib_dir('1Tag Artist', 'Tag Album', 'artifact.file')
    
    def test_prune_empty_directories_with_move_import(self):
        config['import']['move'] = True
        
        self._run_importer()
        
        self.assert_not_in_lib_dir('Tag Artist')

    def test_do_nothing_when_paths_do_not_change_with_copy_import(self):
        self.lib.path_formats = self.original_path_formats
        self._setup_import_session(autotag=False, import_dir=self.lib_dir)
        
        self._run_importer()
        
        self.assert_number_of_files_in_dir(2, self.lib_dir, 'Tag Artist', 'Tag Album')
        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file')

    def test_do_nothing_when_paths_do_not_change_with_move_import(self):
        self.lib.path_formats = self.original_path_formats
        self._setup_import_session(autotag=False, import_dir=self.lib_dir)
        config['import']['move'] = True
        
        self._run_importer()
        
        self.assert_number_of_files_in_dir(2, self.lib_dir, 'Tag Artist', 'Tag Album')
        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file')
    
    def test_rename(self):
        config['paths']['ext:file'] = unicode('$albumpath/$artist - $album')

        self._run_importer()

        self.assert_in_lib_dir('1Tag Artist', 'Tag Album', 'Tag Artist - Tag Album.file')
    
    @unittest.skip('Todo')
    def test_rename_when_paths_do_not_change(self):
        """
        This test considers the situation where the path format for a file extension
        is changed and files already in the library are reimported and renamed to 
        reflect the change
        """
        self.lib.path_formats = self.original_path_formats
        self._setup_import_session(autotag=False, import_dir=self.lib_dir)
        config['paths']['ext:file'] = unicode('$albumpath/$album')
       
        self._run_importer()
        
        self.assert_in_lib_dir('Tag Artist', 'Tag Album', 'Tag Album.file')

class CopyArtifactsFromNestedDirectoryTest(CopyArtifactsTestCase):
    """
    Tests to check that copyartifacts copies or moves artifact files from a nested directory
    structure. i.e. songs in an album are imported from two directories corresponding to disc numbers
    """

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
        
        self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')
        self.assertTrue('Ignored files' not in self.io.getoutput())
 
    def test_print_ignored(self):
        config['copyartifacts']['print_ignored'] = True
        config['copyartifacts']['extensions'] = '.file'
        
        self._run_importer()

        self.assert_not_in_lib_dir('Tag Artist', 'Tag Album', 'artifact.file2')
        self.assertTrue('Ignored files' in self.io.getoutput())

if __name__ == '__main__':
    unittest.main()
