import os
import sys

import beets.util
from beets.ui import get_path_formats
from beets.plugins import BeetsPlugin
from beets.library import DefaultTemplateFunctions
from beets.util.functemplate import Template

class CopyArtifactsPlugin(BeetsPlugin):
    def __init__(self):
        super(CopyArtifactsPlugin, self).__init__()

        self.config.add({
            'extensions': '.*',
            'print_ignored': 'no'
        })

        self.extensions = self.config['extensions'].get().split()
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
        # there has to be a better way of doing this
        album_path = set(os.path.dirname(i.path) for i in task.imported_items())
        album_path = list(album_path)[0]

        mapping = {
            'artist': task.cur_album,
            'album': task.cur_artist,
            'albumpath': album_path
        }

        source_files = []
        ignored_files = []
        for filename in os.listdir(task.paths[0]):
            source_file = os.path.join(task.paths[0], filename)
            if source_file in task.old_paths:
                continue

            if os.path.isfile(source_file):
                file_ext = os.path.splitext(filename)[1]

                if '.*' in self.extensions or file_ext in self.extensions:
                    source_files.append(source_file)
                else:
                    ignored_files.append(source_file)

        if source_files:
            print 'Copying artifacts:'
            for source_file in source_files:
                filename = os.path.basename(source_file)
                dest_file = self._destination(filename, mapping)

                print '   ', os.path.basename(dest_file)
                beets.util.copy(source_file, dest_file)

        if self.print_ignored and ignored_files:
            print 'Ignored files:'
            for f in ignored_files:
                print '   ', os.path.basename(f)

