import os
import pandas as pd


class LocalFileSource:

    def __init__(self, config):
        self.root_dir = config.root_dir
        self.sheet_name_to_concat = config.sheet_name_to_concat
        self.header_row = config.header_row
        self.engine = config.engine

    def get_files(self):
        file_list = []

        for folder_path, _, file_names in os.walk(self.root_dir):
            for file_name in file_names:
                full_path = os.path.join(folder_path, file_name)
                file_list.append(full_path)

        return file_list

    def collect_exel_to_df(self, file_paths):
        df_combined_files = []
        for i in file_paths:
            try:
                df = pd.read_excel(i, sheet_name=self.sheet_name_to_concat, header=self.header_row, engine=self.engine)
                df["__FILENAME__"] = os.path.basename(i)
                df["__FILEPATH__"] = i
                df_combined_files.append(df)

            except Exception as e:
                print(f"Error reading {i}: {e}")

        if not df_combined_files:
            print("DF NOT COMBINED")

        else:
            return pd.concat(df_combined_files, ignore_index=True)
