import os
import sys

import beets.util
from beets import config
from beets.ui import get_path_formats
from beets.mediafile import TYPES
from beets.plugins import BeetsPlugin
from beets.library import DefaultTemplateFunctions
from beets.util.functemplate import Template

__version__ = '1.0-beta.1'
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

        self.register_listener('import_task_files', self.add_artifacts)

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
            file_path = os.path.join(mapping['albumpath'], filename)
            return beets.util.unique_path(file_path)

        if isinstance(path_format, Template):
            subpath_tmpl = path_format
        else:
            subpath_tmpl = Template(path_format)

        # Get template funcs and evaluate against mapping
        funcs = DefaultTemplateFunctions().functions()
        subpath = subpath_tmpl.substitute(mapping, funcs)

        file_path = subpath + file_ext
        return beets.util.unique_path(file_path)

    def add_artifacts(self, task, session):
        imported_item = task.imported_items()[0]
        album_path = os.path.dirname(imported_item.path)

        mapping = {
            'artist': imported_item.artist or 'None',
            'album': imported_item.album or 'None',
            'albumpath': album_path
        }

        source_files = []
        ignored_files = []

        source_path = ''
        try:
            source_path = task.paths[0]
        except TypeError:
            source_path = os.path.dirname(task.old_paths[0])

        for root, dirs, files in beets.util.sorted_walk(
                    source_path, ignore=config['ignore'].as_str_seq()):
            for filename in files:
                source_file = os.path.join(root, filename)

                if source_file in task.old_paths:
                    continue

                file_ext = os.path.splitext(filename)[1]
                if len(file_ext) > 1 and file_ext[1:] in TYPES:
                    continue

                if '.*' in self.extensions or file_ext in self.extensions:
                    source_files.append(source_file)
                else:
                    ignored_files.append(source_file)

        if source_files:
            for source_file in source_files:
                if album_path == os.path.dirname(source_file):
                    continue

                filename = os.path.basename(source_file)
                dest_file = self._destination(filename, mapping)

                if config['import']['move']:
                    self._move_artifact(source_file, dest_file)
                else:
                    if task.replaced_items[imported_item]:
                        # Reimport
                        self._move_artifact(source_file, dest_file)
                        task.prune(source_files[0])
                    else:
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
        dest_file = beets.util.bytestring_path(dest_file)
        print 'Moving artifact: {0}'.format(os.path.basename(dest_file))
        beets.util.move(source_file, dest_file)

