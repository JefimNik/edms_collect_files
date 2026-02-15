import os

import pandas as pd

from DatabaseManager import DatabaseManager
from utils import load_config, print_list_data
import yaml


class RawData:
    def __init__(self, config):
        # ---Paths from config---
        self.root_dir = config["path_data"]["root_dir"]
        self.output_dir = config["path_data"]["output_dir"]

        # --- def variables ---
        self.df = None
        self.file_list = []
        self.error_file_list = []
        self.not_bom_file_list = []
        self.df_combined = pd.DataFrame()
        self.output_path = None
        self.df_errors = None

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
        file_list = []
        for folder_path, _, file_names in os.walk(self.root_dir):
            for file_name in file_names:
                full_path = os.path.join(folder_path, file_name).upper()
                file_list.append(full_path)
        # list
        self.file_list = file_list
        # df
        self.df = pd.DataFrame({"get_file_list": file_list})
        self.df["dir"] = self.df["get_file_list"].apply(os.path.dirname).str.upper()
        self.df["file"] = self.df["get_file_list"].apply(os.path.basename).str.upper()
        self.df["index"] = self.df.index
        return file_list, self.get_file_list.__name__

    def filter_by_folder(self):
        f_name = "filter_by_folder"

        include_dir = [x.upper() for x in self.include_dir]
        exclude_dir = [x.upper() for x in self.exclude_dir]

        # --- file list ---
        if exclude_dir:
            self.file_list = [
                x for x in self.file_list
                if not any(z in os.path.dirname(x).upper() for z in exclude_dir)
            ]

        if include_dir:
            self.file_list = [
                x for x in self.file_list
                if any(z in os.path.dirname(x).upper() for z in include_dir)
            ]

        # --- dataframe ---
        df_temp = self.df[["index", "dir"]].copy()
        df_temp.columns = ["index", f_name]

        if include_dir:
            pattern = "|".join(include_dir)
            df_temp = df_temp[df_temp[f_name].str.contains(pattern, regex=True)]

        if exclude_dir:
            pattern = "|".join(exclude_dir)
            df_temp = df_temp[~df_temp[f_name].str.contains(pattern, regex=True)]

        self.df = self.df.merge(df_temp, left_on="index", right_on="index", how="left")

        return f_name

    def filter_by_filename(self):
        f_name = "filter_by_filename"

        include_file = [x.upper() for x in self.include_file]
        exclude_file = [x.upper() for x in self.exclude_file]

        file_list = self.file_list

        # --- list ---
        if exclude_file:
            file_list = [
                x for x in file_list
                if not any(z in os.path.basename(x).upper() for z in exclude_file)
            ]

        if include_file:
            file_list = [
                x for x in file_list
                if any(z in os.path.basename(x).upper() for z in include_file)
            ]

        self.file_list = file_list

        # --- dataframe ---
        df_temp = self.df[["index", "filter_by_folder", "file"]].copy()
        df_temp.columns = ["index", "filter_by_folder_temp", f_name]

        if include_file:
            pattern = "|".join(include_file)
            df_temp = df_temp[df_temp[f_name].str.contains(pattern, regex=True)]

        if exclude_file:
            pattern = "|".join(exclude_file)
            df_temp = df_temp[~df_temp[f_name].str.contains(pattern, regex=True)]

        self.df = self.df.merge(df_temp, left_on=["index", "dir"], right_on=["index", "filter_by_folder_temp"],
                                how="left")
        self.df = self.df.drop(columns=["filter_by_folder_temp"])

        return f_name

    def remove_duplicates_by_filename(self):
        """
        find same file names and remove last paths from list
        return filtered and dropped paths lists
        """
        f_name = "remove_duplicates_by_filename"

        seen = []
        unique_files = []
        duplicates = []
        for path in self.file_list:
            file_name = os.path.basename(path)
            if file_name not in seen:
                seen.append(file_name)
                unique_files.append(path)
            elif file_name in seen:
                duplicates.append(path)
        self.file_list = unique_files
        # --- dataframe ---
        df_temp = self.df[["index", "filter_by_filename"]].copy()
        df_temp.columns = ["index", f_name]
        df_temp = df_temp.drop_duplicates(subset=[f_name])
        self.df = self.df.merge(df_temp, left_on="index", right_on="index", how="left")

        return unique_files, duplicates

    def filter_by_sheet_names(self):
        """
        filter files by checking sheet names inside
        """
        f_name = "filter_by_sheet_names"

        edms_bom_standard_list = []
        not_bom_file_list = []
        error_file_list = []
        for path in self.file_list:
            try:
                xls = pd.ExcelFile(path, engine="xlrd")
                if all(i in xls.sheet_names for i in self.sheet_names):
                    edms_bom_standard_list.append(path)
                else:
                    not_bom_file_list.append(path)
            except Exception:
                error_file_list.append(path)
        self.file_list = edms_bom_standard_list
        self.not_bom_file_list = not_bom_file_list
        self.error_file_list = error_file_list

        # --- dataframe ---
        df_temp = self.df[["index", "filter_by_folder", "remove_duplicates_by_filename"]].copy()
        df_temp.columns = ["index", "filter_by_folder_temp", f_name]

        mask_valid = pd.Series(False, index=df_temp.index)
        mask_error = pd.Series(False, index=df_temp.index)

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
        self.df = self.df.merge(df_temp, left_on="index", right_on="index", how="left")

        return edms_bom_standard_list, not_bom_file_list, error_file_list

    def make_df_from_excel_files(self):
        """
        collect and combine tables from approved BOM files from BOM sheet, headers on row 5 in Excel (index 4)
        """
        f_name = "make_df_from_excel_files"

        # df_combined = []
        # df_errors = []
        # for i in self.file_list:
        #     try:
        #         df = pd.read_excel(i, sheet_name=self.sheet_name_to_concat, header=self.header_row, engine=self.engine)
        #         df["__FILENAME__"] = os.path.basename(i)
        #         df["__FILEPATH__"] = i
        #         df_combined.append(df)
        #     except Exception:
        #         df_errors.append(i)
        #
        # if not df_combined:
        #     print("DF NOT COMBINED")
        #     df_combined = pd.DataFrame()
        #
        # else:
        #     df_combined = pd.concat(df_combined, ignore_index=True)
        #
        # self.df_combined = df_combined
        # self.df_errors = df_errors

        # --- dataframe ---

        df_temp = self.df[["index", "get_file_list", "filter_by_sheet_names"]].copy()
        df_temp.columns = ["index","get_file_list", f_name]
        df_temp = df_temp.dropna(subset=f_name)

        df_combined = []
        file_list = df_temp["get_file_list"]
        mask_valid = pd.Series(False, index=df_temp.index)

        for id, i in file_list.items():
            try:
                df = pd.read_excel(i, sheet_name=self.sheet_name_to_concat, header=self.header_row, engine=self.engine)
                df["__FILENAME__"] = os.path.basename(i)
                df["__FILEPATH__"] = i
                df_combined.append(df)
                mask_valid.loc[id] = True
            except Exception:
                mask_valid.loc[id] = False

        if not df_combined:
            print("DF NOT COMBINED")

        else:
            df_temp = df_temp[mask_valid]
            df_temp = df_temp.drop(columns=["get_file_list"])
            self.df = self.df.merge(df_temp, left_on="index", right_on="index", how="left")
            self.df_combined = pd.concat(df_combined, ignore_index=True)

        return df_combined

    def df_to_excel(self):
        if not self.df_combined.empty:
            output_path = rf"{self.output_dir}\{self.file_type}_excel_collected.xlsx"
            self.df_combined.to_excel(output_path, index=False)
            self.output_path = output_path
            return output_path
        else:
            print("\nEmpty df_combined, no export to Excel")
            return None

    def run_rawdata_for_excel(self):
        self.get_file_list()
        self.filter_by_folder()
        self.filter_by_filename()
        self.remove_duplicates_by_filename()
        self.filter_by_sheet_names()
        self.make_df_from_excel_files()
        self.df_to_excel()


if __name__ == "__main__":
    config = load_config("config/_config_bom_type1.yaml")
    # data = RawData(config)
    # data.run_rawdata_for_excel()

    print(yaml.dump(config, sort_keys=False, allow_unicode=True))

    data = RawData(config)

    data.get_file_list()
    data.filter_by_folder()
    data.filter_by_filename()
    data.remove_duplicates_by_filename()
    data.filter_by_sheet_names()
    data.make_df_from_excel_files()
    data.df_to_excel()

    db = DatabaseManager(data.output_dir, "db_file_bom")
    db.save_to_db(data.df, "df_steps_list3")
    db.save_to_db(data.df_combined, "df_combined")


    # data = RawData(config)
    # report_file = os.path.join(data.output_dir, "RawData_paths.txt")
    # if os.path.exists(report_file):
    #     os.remove(report_file)
    #
    # print(f"Root: {data.root_dir}")
    # print(f"Output: {data.output_dir}")
    #
    # data.get_file_list()
    # print_list_data(data.file_list, data.output_dir, "get_file_list")
    #
    # data.filter_by_folder()
    # print_list_data(data.file_list, data.output_dir,"filter_by_folder")
    #
    # data.filter_by_filename()
    # print_list_data(data.file_list, data.output_dir,"filter_by_filename")
    #
    # data.remove_duplicates_by_filename()
    # print_list_data(data.file_list, data.output_dir,"remove_duplicates_by_filename")
    #
    # data.filter_by_sheet_names()
    # print_list_data(data.file_list, data.output_dir,"filter_by_sheet_names")
    # print_list_data(data.not_bom_file_list, data.output_dir,"not_bom_file_list")
    # print_list_data(data.error_file_list, data.output_dir,"error_file_list")
    #
    # data.make_df_from_excel_files()
    # print(f"\nDF shape: {data.df_combined.shape}")
    # data.df_to_excel()
    # print(f"\nExcel saved to: {data.output_path}")
    #
    # db = DatabaseManager(data.output_dir, "db_file_bom")
    # db.save_to_db(data.df_combined,"df_combined")
