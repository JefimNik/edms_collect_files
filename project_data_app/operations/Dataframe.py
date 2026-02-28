import os


class LocalFileSource:

    def __init__(self, config):
        self.root_dir = config.root_dir

    def get_files(self):
        file_list = []

        for folder_path, _, file_names in os.walk(self.root_dir):
            for file_name in file_names:
                full_path = os.path.join(folder_path, file_name)
                file_list.append(full_path)

        return file_list
