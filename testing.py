from config import root_dir, output_dir
import os
import pandas as pd

class RawData:
    def __init__(self, root_dir, output_dir):
        self.root_dir = root_dir
        self.output_dir = output_dir

        self.file_list = []

        self.include_file = ["xls"]
        self.exclude_file = []
        self.include_dir = []
        self.exclude_dir = ["_archive"]

        pd.set_option("display.max_columns", 8)
        pd.set_option("display.max_rows", 10)
        pd.set_option("display.max_colwidth", 8)
        pd.set_option("display.width", 150)
        pd.set_option("display.expand_frame_repr", False)

    def get_file_list(self):
        """
        get all paths+filenames from dir folder and make upper case
        """
        temp_file_list = []
        for folder_path, _, file_names in os.walk(self.root_dir):
            for file_name in file_names:
                full_path = os.path.join(folder_path, file_name).upper()
                temp_file_list.append(full_path)
        self.file_list = temp_file_list
        return temp_file_list

    def filter_by_folder_and_filename(self) -> list:
        """
        exclude old and archived folders from list, files with specific names / include folders and files by rule
        """
        include_file = [x.upper() for x in self.include_file]
        include_dir = [x.upper() for x in self.include_dir]
        exclude_file = [x.upper() for x in self.exclude_file]
        exclude_dir = [x.upper() for x in self.exclude_dir]

        file_list = [x for x in file_list if not exclude_dir or not any(z in os.path.dirname(x) for z in exclude_dir)]
        file_list = [x for x in file_list if not include_dir or any(z in os.path.dirname(x) for z in include_dir)]
        file_list = [x for x in file_list if
                     not exclude_file or not any(z in os.path.basename(x) for z in exclude_file)]
        file_list = [x for x in file_list if not include_file or any(z in os.path.basename(x) for z in include_file)]
        return file_list

    def remove_duplicates_by_filename(self) -> tuple[list, list]:
        """
        find same file names and remove last paths from list
        return filtered and dropped paths lists
        """
        seen = []
        unique_files = []
        duplicates = []
        for path in file_list:
            file_name = os.path.basename(path)
            if file_name not in seen:
                seen.append(file_name)
                unique_files.append(path)
            elif file_name in seen:
                duplicates.append(path)
        return unique_files, duplicates
class RawDataBOMType1(RawData):
    def __init__(self, root_dir, output_dir):
        super().__init__(root_dir, output_dir)