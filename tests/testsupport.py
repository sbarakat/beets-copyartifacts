import os
import shutil

from test.test_importer import TestImportSession
from test import _common

from beets import library
from beets import mediafile
from beets import config
from beets import plugins

import logging
log = logging.getLogger("beets")

class CopyArtifactsTestCase(_common.TestCase):
    """
    Provides common setup and teardown, a convenience method for exercising the
    plugin/importer, tools to setup a library, a directory containing files
    that are to be imported and an import session. The class also provides stubs
    for the autotagging library and assertions helpers.
    """
    def setUp(self):
        super(CopyArtifactsTestCase, self).setUp()

        self._setup_library()

        # Install the DummyIO to capture anything directed to stdout
        self.io.install()

    def _run_importer(self):
        """
        Create an instance of the plugin, run the importer, and
        remove/unregister the plugin instance so a new instance can
        be created when this method is run again.
        This is a convenience method that can be called to setup, exercise
        and teardown the system under test after setting any config options
        and before assertions are made regarding changes to the filesystem.
        """
        # Setup
        # Create an instance of the plugin
        plugins.find_plugins()

        # Exercise
        # Run the importer
        self.importer.run()
        # Fake the occurence of the cli_exit event
        plugins.send('cli_exit', lib=self.lib)

        # Teardown
        if plugins._instances:
            classes = list(plugins._classes)

            # Unregister listners
            for event in classes[0].listeners:
                del classes[0].listeners[event][0]

            # Delete the plugin instance so a new one gets created for each test
            del plugins._instances[classes[0]]

        log.debug("--- library structure")
        self._list_files(self.lib_dir)

    def _setup_library(self):
        self.lib_db = os.path.join(self.temp_dir, 'testlib.blb')
        self.lib_dir = os.path.join(self.temp_dir, 'testlib_dir')
        os.mkdir(self.lib_dir)

        self.lib = library.Library(self.lib_db)
        self.lib.directory = self.lib_dir
        self.lib.path_formats = [
            (u'default', os.path.join(u'$artist', u'$album', u'$title')),
            (u'singleton:true', os.path.join(u'singletons', u'$title')),
            (u'comp:true', os.path.join(u'compilations', u'$album', u'$title')),
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
        self._set_import_dir()

        album_path = os.path.join(self.import_dir, 'the_album')
        os.makedirs(album_path)

        # Create artifact
        open(os.path.join(album_path, 'artifact.file'), 'a').close()
        open(os.path.join(album_path, 'artifact.file2'), 'a').close()

        medium = self._create_medium(os.path.join(album_path, 'track_1.mp3'), 'full.mp3')
        self.import_media = [medium]

        log.debug("--- import directory created")
        self._list_files(album_path)

    def _create_medium(self, path, resource_name, album=None):
        """
        Creates and saves a media file object located at path using resource_name
        from the beets test resources directory as initial data
        """

        resource_path = os.path.join(_common.RSRC, resource_name)

        metadata = {
                     'artist': 'Tag Artist',
                     'album':  album or 'Tag Album',
                     'albumartist':  None,
                     'mb_trackid': None,
                     'mb_albumid': None,
                     'comp': None
                   }

        # Copy media file
        shutil.copy(resource_path, path)
        medium = mediafile.MediaFile(path)

        # Set metadata
        metadata['track'] = 1
        metadata['title'] = 'Tag Title 1'
        for attr in metadata:
            setattr(medium, attr, metadata[attr])
        medium.save()

        return medium

    def _set_import_dir(self):
        """
        Sets the import_dir and ensures that it is empty.
        """
        self.import_dir = os.path.join(self.temp_dir, 'testsrcdir')
        if os.path.isdir(self.import_dir):
            shutil.rmtree(self.import_dir)

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
                                loghandler=None,
                                paths=[import_dir or self.import_dir],
                                query=None)

    def _list_files(self, startpath):
        for root, dirs, files in os.walk(startpath):
            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            log.debug('{}{}/'.format(indent, os.path.basename(root)))
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                log.debug('{}{}'.format(subindent, f))

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
        Assert that there are ``count`` files in path formed by joining ``segments``
        """
        self.assertEqual(len([name for name in os.listdir(os.path.join(*segments))]), count)

