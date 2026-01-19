import os
import pandas as pd
from utils import load_config, print_list_data


class RawData:
    def __init__(self, config):
        # ---Paths from config---
        self.root_dir = config["path_data"]["root_dir"]
        self.output_dir = config["path_data"]["output_dir"]

        # --- def variables ---
        self.file_list = []
        self.edms_bom_standard_list = []
        self.edms_bom_axima_list = []
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
        self.file_list = file_list
        return file_list

    def filter_by_folder(self):
        """
        exclude old and archived folders from list, files with specific names / include folders and files by rule
        """
        include_dir = [x.upper() for x in self.include_dir]
        exclude_dir = [x.upper() for x in self.exclude_dir]

        file_list = self.file_list
        file_list = [x for x in file_list if not exclude_dir or not any(z in os.path.dirname(x) for z in exclude_dir)]
        file_list = [x for x in file_list if not include_dir or any(z in os.path.dirname(x) for z in include_dir)]
        self.file_list = file_list
        return file_list

    def filter_by_filename(self):
        """
        exclude old and archived folders from list, files with specific names / include folders and files by rule
        """
        include_file = [x.upper() for x in self.include_file]
        exclude_file = [x.upper() for x in self.exclude_file]

        file_list = self.file_list
        file_list = [x for x in file_list if
                     not exclude_file or not any(z in os.path.basename(x) for z in exclude_file)]
        file_list = [x for x in file_list if not include_file or any(z in os.path.basename(x) for z in include_file)]
        self.file_list = file_list
        return file_list

    def remove_duplicates_by_filename(self):
        """
        find same file names and remove last paths from list
        return filtered and dropped paths lists
        """
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
        return unique_files, duplicates

    # def filter_by_sheet_names(self):
    #     """
    #     filter files by checking sheet names inside
    #     """
    #     edms_bom_standard_list = []
    #     not_bom_file_list = []
    #     error_file_list = []
    #     for path in self.file_list:
    #         try:
    #             xls = pd.ExcelFile(path, engine="xlrd")
    #             if all(i in xls.sheet_names for i in self.sheet_names):
    #                 edms_bom_standard_list.append(path)
    #             else:
    #                 not_bom_file_list.append(path)
    #         except Exception:
    #             error_file_list.append(path)
    #     self.file_list = edms_bom_standard_list
    #     self.not_bom_file_list = not_bom_file_list
    #     self.error_file_list = error_file_list
    #     return edms_bom_standard_list, not_bom_file_list, error_file_list

    def filter_by_sheet_names(self):
        """
        filter files by checking sheet names inside
        """
        edms_bom_standard_list = []
        edms_bom_axima_list = []
        not_bom_file_list = []
        error_file_list = []
        for path in self.file_list:
            if path.suffix == ".XLS":
                try:
                    xls = pd.ExcelFile(path, engine="xlrd")
                    if all(i in xls.sheet_names for i in self.sheet_names):
                        edms_bom_standard_list.append(path)
                    else:
                        not_bom_file_list.append(path)
                except Exception:
                    error_file_list.append(path)
            elif path.suffix == ".XLSM" or path.suffix == ".XLSX":
                try:
                    xls = pd.ExcelFile(path, engine="openpyxl")
                    if all(i in xls.sheet_names for i in self.sheet_names):
                        edms_bom_axima_list.append(path)
                    else:
                        not_bom_file_list.append(path)
                except Exception:
                    error_file_list.append(path)


        self.file_list = edms_bom_standard_list
        self.edms_bom_axima_list = edms_bom_axima_list
        self.not_bom_file_list = not_bom_file_list
        self.error_file_list = error_file_list
        return edms_bom_standard_list, edms_bom_axima_list, not_bom_file_list, error_file_list

    def make_df_from_excel_files(self):
        """
        collect and combine tables from approved BOM files from BOM sheet, headers on row 5 in Excel (index 4)
        """
        df_combined = []
        df_errors = []
        for i in self.file_list:
            try:
                df = pd.read_excel(i, sheet_name=self.sheet_name_to_concat, header=self.header_row, engine=self.engine)
                df["__FILENAME__"] = os.path.basename(i)
                df["__FILEPATH__"] = i
                df_combined.append(df)
            except Exception:
                df_errors.append(i)

        if not df_combined:
            print("DF NOT COMBINED")
            df_combined = pd.DataFrame()

        else:
            df_combined = pd.concat(df_combined, ignore_index=True)

        self.df_combined = df_combined
        self.df_errors = df_errors
        return df_combined, df_errors



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
    config = load_config("_config_bom_type1.yaml")
    # data = RawData(config)
    # data.run_rawdata_for_excel()

    print("--CONFIG--")
    for i in config.items():
        print(i)
    print("")

    data = RawData(config)

    print(f"Root: {data.root_dir}")
    print(f"Output: {data.output_dir}")

    data.get_file_list()
    print_list_data(data.file_list, data.output_dir, "get_file_list")

    data.filter_by_folder()
    print_list_data(data.file_list, data.output_dir,"filter_by_folder")

    data.filter_by_filename()
    print_list_data(data.file_list, data.output_dir,"filter_by_filename")

    data.remove_duplicates_by_filename()
    print_list_data(data.file_list, data.output_dir,"remove_duplicates_by_filename")

    data.filter_by_sheet_names()
    print_list_data(data.edms_bom_standard_list, data.output_dir,"edms_standard_list")
    print_list_data(data.edms_bom_axima_list, data.output_dir,"edms_pdg_axima_list")
    print_list_data(data.not_bom_file_list, data.output_dir,"not_type_file_list")
    print_list_data(data.error_file_list, data.output_dir,"error_file_list")

    data.make_df_from_excel_files()
    print(f"\nDF shape: {data.df_combined.shape}")
    data.df_to_excel()
    print(f"\nExcel saved to: {data.output_path}")
