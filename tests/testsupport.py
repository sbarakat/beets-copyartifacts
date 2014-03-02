import os
import shutil

from test.test_importer import TestImportSession
from test import _common

from beets import library
from beets import mediafile
from beets import config
from beets import plugins

class CopyArtifactsTestCase(_common.TestCase):
    """
    Provides common setup and teardown, tools to setup a library, a directory
    containing files that are to be imported and an import session. The class
    also provides stubs for the autotagging library and assertions helpers.
    """
    def setUp(self):
        super(CopyArtifactsTestCase, self).setUp()
        
        self._setup_library()
        
        # Install the DummyIO to capture anything directed to stdout
        self.io.install()

        # Create an instance of the plugin
        plugins.find_plugins()

    def tearDown(self):
        # Unregister listners
        del plugins._classes[0].listeners['import_task_files'][0]

        # Delete the plugin instance so a new one gets created for each test
        del plugins._instances[plugins._classes[0]]

        super(CopyArtifactsTestCase, self).tearDown()

    def _setup_library(self):
        self.lib_db = os.path.join(self.temp_dir, 'testlib.blb')
        self.lib_dir = os.path.join(self.temp_dir, 'testlib_dir')
        os.mkdir(self.lib_dir)

        self.lib = library.Library(self.lib_db)
        self.lib.directory =self.lib_dir
        self.lib.path_formats = [
            ('default', os.path.join('$artist', '$album', '$title')),
            ('singleton:true', os.path.join('singletons', '$title')),
            ('comp:true', os.path.join('compilations','$album', '$title')),
        ]

    def _create_flat_import_dir(self):
        """
        Creates a directory with media files and artifacts.
        Sets ``self.import_dir`` to the path of the directory. Also sets
        ``self.import_media`` to a list :class:`MediaFile` for all the media files in
        the directory.

        The directory has the following layout
          the_album/
            track_1.mp3
            artifact.file
            artifact.file2
        """
        self.import_dir = os.path.join(self.temp_dir, 'testsrcdir')
        if os.path.isdir(self.import_dir):
            shutil.rmtree(self.import_dir)

        album_path = os.path.join(self.import_dir, 'the_album')
        os.makedirs(album_path)

        resource_path = os.path.join(_common.RSRC, 'full.mp3')

        metadata = {
                     'artist': 'Tag Artist',
                     'album':  'Tag Album',
                     'albumartist':  None,
                     'mb_trackid': None,
                     'mb_albumid': None,
                     'comp': None
                   }

        # Copy media file
        medium_path = os.path.join(album_path, 'track_1.mp3')
        shutil.copy(resource_path, medium_path)
        medium = mediafile.MediaFile(medium_path)

        # Set metadata
        metadata['track'] = 1
        metadata['title'] = 'Tag Title 1'
        for attr in metadata: setattr(medium, attr, metadata[attr])
        medium.save()

        # Create artifact
        open(os.path.join(album_path, 'artifact.file'), 'a').close()
        open(os.path.join(album_path, 'artifact.file2'), 'a').close()
        
        self.import_media = [medium]

    def _create_nested_import_dir(self):
        """
        Creates a directory with media files and artifacts nested in subdirectories.
        Sets ``self.import_dir`` to the path of the directory. Also sets
        ``self.import_media`` to a list :class:`MediaFile` for all the media files in
        the directory.

        The directory has the following layout
          the_album/
            disc1/
              track_1.mp3
              artifact1.file
            disc2/
              track_1.mp3
              artifact2.file
        """
    def _setup_import_session(self, import_dir=None,
            delete=False, threaded=False, copy=True,
            singletons=False, move=False, autotag=True):
        config['import']['copy'] = copy
        config['import']['delete'] = delete
        config['import']['timid'] = True
        config['threaded'] = False
        config['import']['singletons'] = singletons
        config['import']['move'] = move
        config['import']['autotag'] = autotag
        config['import']['resume'] = False

        self.importer = TestImportSession(self.lib,
                                logfile=None,
                                paths=[import_dir or self.import_dir],
                                query=None)
    
    def assert_in_lib_dir(self, *segments):
        """
        Join the ``segments`` and assert that this path exists in the library
        directory
        """
        self.assertExists(os.path.join(self.lib_dir, *segments))

    def assert_not_in_lib_dir(self, *segments):
        """
        Join the ``segments`` and assert that this path does not exist in
        the library directory
        """
        self.assertNotExists(os.path.join(self.lib_dir, *segments))

    def assert_in_import_dir(self, *segments):
        """
        Join the ``segments`` and assert that this path exists in the import 
        directory
        """
        self.assertExists(os.path.join(self.import_dir, *segments))

    def assert_not_in_import_dir(self, *segments):
        """
        Join the ``segments`` and assert that this path does not exist in
        the library directory
        """
        self.assertNotExists(os.path.join(self.import_dir, *segments))

    def assert_number_of_files_in_dir(self, count, *segments):
        """
        Assert that there are ``count`` files in ``path``
        """
        self.assertEqual(len([name for name in os.listdir(os.path.join(*segments))]), count)
