import os

import beets.util
from beets.plugins import BeetsPlugin

class CopyArtifactsPlugin(BeetsPlugin):
    def __init__(self):
        super(CopyArtifactsPlugin, self).__init__()

        self.config.add({
            'extensions': '.*',
            'print_ignored': 'no'
        })

        self.extensions = self.config['extensions'].get().split()
        self.print_ignored = self.config['print_ignored'].get()

        self.register_listener('import_task_files', self.add_artifacts)

    def add_artifacts(self, task, session):
        # there has to be a better way of doing this
        dest_path = set(os.path.dirname(i.path) for i in task.imported_items())
        dest_path = list(dest_path)[0]

        source_files = []
        ignored_files = []
        for filename in os.listdir(task.paths[0]):
            source_file = os.path.join(task.paths[0], filename)
            if source_file in task.old_paths:
                continue

            if os.path.isfile(source_file):
                ext = os.path.splitext(filename)[1]

                if '.*' in self.extensions or ext in self.extensions:
                    source_files.append(source_file)
                else:
                    ignored_files.append(source_file)

        if source_files:
            print 'Copying artifacts:'
            for source_file in source_files:
                filename = os.path.basename(source_file)
                dest_file = beets.util.unique_path(os.path.join(dest_path, filename))

                print '   ', os.path.basename(dest_file)
                beets.util.copy(source_file, dest_file)

        if self.print_ignored and ignored_files:
            print 'Ignored files:'
            for f in ignored_files:
                print '   ', os.path.basename(f)

