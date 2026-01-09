# python -m pip install --upgrade pip setuptools wheel
# pip install xlrd

import os
import pandas as pd

def get_file_list(root_dir: str) ->list:
    '''
    get all paths+filenames from dir folder and make upper case
    '''
    file_list = []
    for folder_path, _, file_names in os.walk(root_dir):
        for file_name in file_names:
                full_path = os.path.join(folder_path, file_name).upper()
                file_list.append(full_path)
    return file_list

def filter_by_folder_and_filename(file_list: list, include_file, include_dir, exclude_file, exclude_dir) -> list:
    '''
    exclude old and archived folders from list, files with specific names / include folders and files by rule
    '''
    include_file = [x.upper() for x in include_file]
    include_dir = [x.upper() for x in include_dir]
    exclude_file = [x.upper() for x in exclude_file]
    exclude_dir = [x.upper() for x in exclude_dir]

    file_list = [x for x in file_list if not exclude_dir or not any(z in os.path.dirname(x) for z in exclude_dir)]
    file_list = [x for x in file_list if not include_dir or any(z in os.path.dirname(x) for z in include_dir)]
    file_list = [x for x in file_list if not exclude_file or not any(z in os.path.basename(x) for z in exclude_file)]
    file_list = [x for x in file_list if not include_file or any(z in os.path.basename(x) for z in include_file)]
    return file_list

def remove_duplicates_by_filename(all_files: list) -> tuple[list, list]:
    seen = []
    unique_files = []
    duplicates = []
    for path in all_files:
        file_name = os.path.basename(path)
        if file_name not in seen:
            seen.append(file_name)
            unique_files.append(path)
        elif file_name in seen:
            duplicates.append(path)
    return unique_files, duplicates

def filter_by_sheet_names(all_files: list) -> tuple:
    edms_bom_standard_list = []
    not_bom_file_list = []
    sheet_names = ["Summary", "BOM", "Error", "Warning", "Status"]

    for path in all_files:
        try:
            xls = pd.ExcelFile(path, engine="xlrd")
            if all(i in xls.sheet_names for i in sheet_names):
                edms_bom_standard_list.append(path)
        except:
            not_bom_file_list.append(path)

    return edms_bom_standard_list, not_bom_file_list





if __name__=="__main__":
    root_dir = r"C:\Users\user\Vilesco\DATA_CORE - Документы\Z34\Z34 CDA HVAC MFZ 1-2\RAW\TUY\EDMS\TUSNA"

    include_file = ["xls"]
    exclude_file = []

    include_dir = []
    exclude_dir = ["_archive"]


    path_corrections_bom = ["BOM", "RPT", "BUM", "BOB", "RTP"] #

    all_files = get_file_list(root_dir)
    print(f"LEN all_files: {len(all_files)}")

    all_files = filter_by_folder_and_filename(all_files, include_file, exclude_file, include_dir, exclude_dir)
    print(f"LEN all_files after include/ex: {len(all_files)}")
    for i in all_files:
        print(i)

    # all_files, duplicates = remove_duplicates_by_filename(all_files)
    # print(f"LEN all_files after remove duplicates in file names: {len(all_files)}")
    # if duplicates:
    #     print("Found duplicates")
    #     for i in duplicates:
    #         print(i)
    # else:
    #     print("No duplicates")
    #
    # print("")
    #
    # all_files,not_bom_file_list = filter_by_sheet_names(all_files)
    # print(f"filter_edms_bom_files_by_sheets LEN: {len(all_files)}")
    #
    # if all_files:
    #     print("all_files")
    #     for i in all_files:
    #         print(i)
    # else:
    #     print("No all_files")
    #
    # if not_bom_file_list:
    #     print("not_bom_file_list")
    #     for i in not_bom_file_list:
    #         print(i)
    # else:
    #     print("No not_bom_file_list")