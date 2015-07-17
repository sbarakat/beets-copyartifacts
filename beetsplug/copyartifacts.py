import os
import sys
import filecmp

import beets.util
from beets import config
from beets.ui import get_path_formats
from beets.mediafile import TYPES
from beets.plugins import BeetsPlugin
from beets.library import DefaultTemplateFunctions
from beets.util.functemplate import Template

__version__ = '0.1.2'
__author__ = 'Sami Barakat <sami@sbarakat.co.uk>'

class CopyArtifactsPlugin(BeetsPlugin):
    def __init__(self):
        super(CopyArtifactsPlugin, self).__init__()

        self.config.add({
            'extensions': '.*',
            'print_ignored': False
        })

        self.extensions = self.config['extensions'].as_str_seq()
        self.print_ignored = self.config['print_ignored'].get()

        self.path_formats = [c for c in beets.ui.get_path_formats() if c[0][:4] == u'ext:']

        self.register_listener('import_task_files', self.import_event)
        #XXX: self.register_listener('item_moved', self.move_event)

    def _destination(self, filename, mapping):
        '''Returns a destination path a file should be moved to. The filename
        is unique to ensure files aren't overwritten. This also checks the
        config for path formats based on file extension allowing the use of
        beets' template functions. If no path formats are found for the file
        extension the original filename is used with the album path.
            - ripped from beets/library.py
        '''
        file_ext = os.path.splitext(filename)[1]

        for query, path_format in self.path_formats:
            query_ext = '.' + query[4:]
            if query_ext == file_ext:
                break
        else:
            # No query matched; use original filename
            file_path = os.path.join(mapping['albumpath'],
                                     beets.util.displayable_path(filename))
            return file_path

        if isinstance(path_format, Template):
            subpath_tmpl = path_format
        else:
            subpath_tmpl = Template(path_format)

        # Get template funcs and evaluate against mapping
        funcs = DefaultTemplateFunctions().functions()
        file_path = subpath_tmpl.substitute(mapping, funcs) + file_ext
        return file_path

    def _format(self, value):
        '''Replace path separators in value
            - ripped from beets/dbcore/db.py
        '''
        sep_repl = beets.config['path_sep_replace'].get(unicode)
        for sep in (os.path.sep, os.path.altsep):
            if sep:
                value = value.replace(sep, sep_repl)

        return value

    def _generate_mapping(self, imported_item, album_path):
        mapping = {
            'artist': imported_item.artist or u'None',
            'albumartist': imported_item.albumartist or u'None',
            'album': imported_item.album or u'None',
        }
        for key in mapping:
            mapping[key] = self._format(mapping[key])
        mapping['albumpath'] = beets.util.displayable_path(album_path)
        return mapping

    def import_event(self, task, session):
        imported_item = task.imported_items()[0]
        album_path = os.path.dirname(imported_item.path)

        source_files = []
        ignored_files = []
        reimport = False

        source_path = ''
        try:
            source_path = task.paths[0]
        except TypeError:
            source_path = os.path.dirname(task.old_paths[0])

        for root, dirs, files in beets.util.sorted_walk(
                    source_path, ignore=config['ignore'].as_str_seq()):
            for filename in files:
                source_file = os.path.join(root, filename)

                # Skip music files (already imported)
                if source_file in task.old_paths:
                    continue

                # Skip file, usually reimports to same dir
                if album_path == os.path.dirname(source_file):
                    continue

                # Skip any files extensions handled by beets
                file_ext = os.path.splitext(filename)[1]
                if len(file_ext) > 1 and file_ext[1:] in TYPES:
                    continue

                if '.*' in self.extensions or file_ext in self.extensions:
                    source_files.append(source_file)
                else:
                    ignored_files.append(source_file)

        mapping = self._generate_mapping(imported_item, album_path)
        if task.replaced_items[imported_item]:
            # these will be reimports when dir has changed
            reimport = True

        self.process_artifacts(source_path, source_files, ignored_files, reimport, mapping)

    def move_event(self, item, source, destination):
        print '-------------------------------------'
        source_path = os.path.dirname(source)

        source_files = []
        ignored_files = []

        for root, dirs, files in beets.util.sorted_walk(
                    source_path, ignore=config['ignore'].as_str_seq()):
            for filename in files:
                source_file = os.path.join(root, filename)

                file_ext = os.path.splitext(filename)[1]
                if len(file_ext) > 1 and file_ext[1:] in TYPES:
                    continue
                #print filename

                if '.*' in self.extensions or file_ext in self.extensions:
                    source_files.append(source_file)
                else:
                    ignored_files.append(source_file)

        print source_files
        print ignored_files

    def process_artifacts(self, source_path, source_files, ignored_files, reimport=False, mapping=None):

        if source_files:
            for source_file in source_files:

                filename = source_file[len(source_path)+1:]
                if mapping:
                    dest_file = self._destination(filename, mapping)
                else:
                    pass #XXX: set dest_file

                if (os.path.exists(dest_file)
                    and filecmp.cmp(source_file, dest_file)):
                    # Skip file as it already exists in dest
                    ignored_files.append(source_file)
                    continue

                dest_file = beets.util.unique_path(dest_file)
                beets.util.mkdirall(dest_file)

                if config['import']['move']:
                    self._move_artifact(source_file, dest_file)
                else:
                    if reimport:
                        # This is a reimport
                        # files are already in the library directory
                        self._move_artifact(source_file, dest_file)
                        #TODO: add prune empty source dirs
                    else:
                        # A normal import, just copy
                        self._copy_artifact(source_file, dest_file)


        if self.print_ignored and ignored_files:
            print 'Ignored files:'
            for f in ignored_files:
                print '   ', os.path.basename(f)

    def _copy_artifact(self, source_file, dest_file):
        dest_file = beets.util.bytestring_path(dest_file)
        print 'Copying artifact: {0}'.format(os.path.basename(dest_file))
        beets.util.copy(source_file, dest_file)

    def _move_artifact(self, source_file, dest_file):
        if not os.path.exists(source_file):
            # Sanity check for other plugins moving files
            return

        dest_file = beets.util.bytestring_path(dest_file)
        print 'Moving artifact: {0}'.format(os.path.basename(dest_file))
        beets.util.move(source_file, dest_file)

