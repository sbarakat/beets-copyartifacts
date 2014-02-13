import os
import shutil

from beets.plugins import BeetsPlugin

class CopyArtifactsPlugin(BeetsPlugin):
    def __init__(self):
        super(CopyArtifactsPlugin, self).__init__()

        self.register_listener('import_task_files', self.add_artifacts)

    def _find_valid_filename(self, file_path):
        if os.path.exists(file_path):
            path = os.path.dirname(file_path)
            filename = os.path.basename(file_path)

            split = os.path.splitext(filename)
            for i in range(1, 3330):
                try_file = '.{0}'.format(i).join(split)
                if not os.path.exists(os.path.join(path, try_file)):
                    file_path = os.path.join(path, try_file)
                    return file_path
            else:
                return None

        return file_path

    def add_artifacts(self, task, session):
        dest_path = list(set(os.path.dirname(i.path) for i in task.imported_items()))[0]

        source_files = []
        for source_file in os.listdir(task.paths[0]):
            source_file = os.path.join(task.paths[0], source_file)
            if source_file in task.old_paths:
                continue

            if os.path.isfile(source_file):
                source_files.append(source_file)

        if source_files:
            print 'Copying artifacts...'
            for source_file in source_files:
                filename = os.path.basename(source_file)

                dest_file = os.path.join(dest_path, filename)
                dest_file = self._find_valid_filename(dest_file)

                if dest_file:
                    print '   ', os.path.basename(dest_file)
                    shutil.copy2(source_file, dest_file)
                else:
                    print 'Error: too many artifacts exist with the same filename, not copying', filename

