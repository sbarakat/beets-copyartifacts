import os
import shutil

from test.test_importer import TestImportSession
from test import _common

from beets import library
from beets import mediafile
from beets import config

class ImportHelper(object):
    """
    Provides tools to setup a library, a directory containing files that are
    to be imported and an import session. The class also provides stubs for the
    autotagging library and several assertions for the library.
    """

    def _setup_library(self):
        self.libdb = os.path.join(self.temp_dir, 'testlib.blb')
        self.libdir = os.path.join(self.temp_dir, 'testlibdir')
        os.mkdir(self.libdir)

        self.lib = library.Library(self.libdb)
        self.lib.directory =self.libdir
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
        artifact_path = os.path.join(album_path, 'artifact.file')
        open(artifact_path, 'a').close()
        
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
    def _create_import_dir(self, count=3):
        """
        Creates a directory with media files to import.
        Sets ``self.import_dir`` to the path of the directory. Also sets
        ``self.import_media`` to a list :class:`MediaFile` for all the files in
        the directory.

        The directory has following layout
          the_album/
            track_1.mp3
            track_2.mp3
            track_3.mp3

        :param count:  Number of files to create
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
        self.media_files = []
        for i in range(count):
            # Copy files
            medium_path = os.path.join(album_path, 'track_%d.mp3' % (i+1))
            shutil.copy(resource_path, medium_path)
            medium = mediafile.MediaFile(medium_path)

            # Set metadata
            metadata['track'] = i+1
            metadata['title'] = 'Tag Title %d' % (i+1)
            for attr in metadata: setattr(medium, attr, metadata[attr])
            medium.save()
            self.media_files.append(medium)
        self.import_media = self.media_files

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


