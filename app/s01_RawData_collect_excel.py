import os
import pandas as pd
import yaml
from tqdm import tqdm

from _DatabaseManager import DatabaseManager
from _utils import load_config, config_to_df


class RawData:
    def __init__(self, config):

        # --- Class variables---
        self.df_collect_steps = None
        self.df_combined_files = None

        # ---Paths from config---
        self.root_dir = config["path_data"]["root_dir"]
        self.output_dir = config["path_data"]["output_dir"]

        # --- config variables---
        self.file_type = config["collect_data"]["file_type"]
        self.include_file = config["collect_data"]["include_file"]
        self.exclude_file = config["collect_data"]["exclude_file"]
        self.include_dir = config["collect_data"]["include_dir"]
        self.exclude_dir = config["collect_data"]["exclude_dir"]
        self.sheet_names = config["collect_data"]["sheet_names"]
        self.sheet_name_to_concat = config["collect_data"]["sheet_name_to_concat"]
        self.header_row = config["collect_data"]["header_row"]
        self.engine = config["collect_data"]["engine"]

    def get_file_list(self):
        """
        get all paths+filenames from dir folder and make upper case
        """
        f_name = "get_file_list"
        file_list = []

        for folder_path, _, file_names in os.walk(self.root_dir):
            for file_name in file_names:
                full_path = os.path.join(folder_path, file_name).upper()
                file_list.append(full_path)

        self.df_collect_steps = pd.DataFrame({f_name: file_list})
        self.df_collect_steps["index"] = self.df_collect_steps.index
        self.df_collect_steps["dir"] = self.df_collect_steps[f_name].apply(os.path.dirname).str.upper()
        self.df_collect_steps["file"] = self.df_collect_steps[f_name].apply(os.path.basename).str.upper()
        return None

    def filter_by_folder(self):
        f_name = "filter_by_folder"

        include_dir = [x.upper() for x in self.include_dir]
        exclude_dir = [x.upper() for x in self.exclude_dir]

        df_temp = self.df_collect_steps[["index", "dir"]].copy()
        df_temp.columns = ["index", f_name]

        if include_dir:
            pattern = "|".join(include_dir)
            df_temp = df_temp[df_temp[f_name].str.contains(pattern, regex=True)]

        if exclude_dir:
            pattern = "|".join(exclude_dir)
            df_temp = df_temp[~df_temp[f_name].str.contains(pattern, regex=True)]

        self.df_collect_steps = self.df_collect_steps.merge(df_temp, left_on="index", right_on="index", how="left")

        return None

    def filter_by_filename(self):
        f_name = "filter_by_filename"

        include_file = [x.upper() for x in self.include_file]
        exclude_file = [x.upper() for x in self.exclude_file]

        df_temp = self.df_collect_steps[["index", "filter_by_folder", "file"]].copy()
        df_temp.columns = ["index", "filter_by_folder_temp", f_name]

        if include_file:
            pattern = "|".join(include_file)
            df_temp = df_temp[df_temp[f_name].str.contains(pattern, regex=True)]

        if exclude_file:
            pattern = "|".join(exclude_file)
            df_temp = df_temp[~df_temp[f_name].str.contains(pattern, regex=True)]

        self.df_collect_steps = self.df_collect_steps.merge(df_temp, left_on=["index", "dir"],
                                                            right_on=["index", "filter_by_folder_temp"],
                                                            how="left")
        self.df_collect_steps = self.df_collect_steps.drop(columns=["filter_by_folder_temp"])

        return f_name

    def remove_duplicates_by_filename(self):
        """
        find same file names and remove last paths from list
        return filtered and dropped paths lists
        """
        f_name = "remove_duplicates_by_filename"

        # --- dataframe ---
        df_temp = self.df_collect_steps[["index", "filter_by_filename"]].copy()
        df_temp.columns = ["index", f_name]
        df_temp = df_temp.drop_duplicates(subset=[f_name])
        self.df_collect_steps = self.df_collect_steps.merge(df_temp, left_on="index", right_on="index", how="left")

        return None

    def filter_by_sheet_names(self):
        """
        filter files by checking sheet names inside
        """
        f_name = "filter_by_sheet_names"

        df_temp = self.df_collect_steps[["index", "filter_by_folder", "remove_duplicates_by_filename"]].copy()
        df_temp.columns = ["index", "filter_by_folder_temp", f_name]

        mask_valid = pd.Series(False, index=df_temp.index)

        for id, row in df_temp.iterrows():
            folder_path = row["filter_by_folder_temp"]
            file_name = row[f_name]

            if pd.isna(folder_path) or pd.isna(file_name):
                continue
            full_path = os.path.join(folder_path, file_name)

            try:
                xls = pd.ExcelFile(full_path, engine=self.engine)
                if all(sheet in xls.sheet_names for sheet in self.sheet_names):
                    mask_valid.loc[id] = True
            except Exception:
                mask_valid.loc[id] = False

        df_temp = df_temp[mask_valid]
        df_temp = df_temp.drop(columns=["filter_by_folder_temp"])
        self.df_collect_steps = self.df_collect_steps.merge(df_temp, left_on="index", right_on="index", how="left")

        return None

    def make_df_from_excel_files(self):
        """
        collect and combine tables from approved BOM files from BOM sheet, headers on row 5 in Excel (index 4)
        """
        f_name = "make_df_from_excel_files"

        df_temp = self.df_collect_steps[["index", "get_file_list", "filter_by_sheet_names"]].copy()
        df_temp.columns = ["index", "get_file_list", f_name]
        df_temp = df_temp.dropna(subset=f_name)

        df_combined_files = []
        file_list = df_temp["get_file_list"]
        mask_valid = pd.Series(False, index=df_temp.index)

        for id, i in file_list.items():
            try:
                df = pd.read_excel(i, sheet_name=self.sheet_name_to_concat, header=self.header_row, engine=self.engine)
                df["__FILENAME__"] = os.path.basename(i)
                df["__FILEPATH__"] = i
                df_combined_files.append(df)
                mask_valid.loc[id] = True
            except Exception:
                mask_valid.loc[id] = False

        if not df_combined_files:
            print("DF NOT COMBINED")

        else:
            df_temp = df_temp[mask_valid]
            df_temp = df_temp.drop(columns=["get_file_list"])
            self.df_collect_steps = self.df_collect_steps.merge(df_temp, left_on="index", right_on="index", how="left")
            self.df_combined_files = pd.concat(df_combined_files, ignore_index=True)
        return None

    def df_to_excel(self): # use db_tables_to_excel from _DatabaseManager
        if not self.df_combined_files.empty:
            output_path = rf"{self.output_dir}\{self.file_type}_excel_collected.xlsx"
            self.df_combined_files.to_excel(output_path, index=False)
            self.output_path = output_path
            return output_path
        else:
            print("\nEmpty df_combined_files, no export to Excel")
            return None

    def run_rawdata(self):
        steps = [
            self.get_file_list,
            self.filter_by_folder,
            self.filter_by_filename,
            self.remove_duplicates_by_filename,
            self.filter_by_sheet_names,
            self.make_df_from_excel_files,

        ]
        for i, step in enumerate(steps, start=1):
            step()
            print(f"{i}. {step.__name__}: finished")


if __name__ == "__main__":
    config = load_config("config/_config_bom_type1.yaml")
    output_dir, df_config = config_to_df(config)
    print(yaml.dump(config, sort_keys=False, allow_unicode=True))

    data = RawData(config)
    data.run_rawdata()

    db = DatabaseManager(data.output_dir, "pipeline.db")
    db.save_to_db(data.df_collect_steps, "Collect_files")
    db.save_to_db(data.df_combined_files, "Combine_files")

    tables_list = db.db_table_list()
    db.db_tables_to_excel(tables_list, output_dir, df_config=df_config)
