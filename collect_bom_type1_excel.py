# python -m pip install --upgrade pip setuptools wheel
# pip install xlrd

import os
import pandas as pd

def get_file_list(root_dir: str) ->list:
    """
    get all paths+filenames from dir folder and make upper case
    """
    file_list = []
    for folder_path, _, file_names in os.walk(root_dir):
        for file_name in file_names:
                full_path = os.path.join(folder_path, file_name).upper()
                file_list.append(full_path)
    return file_list

def filter_by_folder_and_filename(file_list: list, include_file, include_dir, exclude_file, exclude_dir) -> list:
    """
    exclude old and archived folders from list, files with specific names / include folders and files by rule
    """
    include_file = [x.upper() for x in include_file]
    include_dir = [x.upper() for x in include_dir]
    exclude_file = [x.upper() for x in exclude_file]
    exclude_dir = [x.upper() for x in exclude_dir]

    file_list = [x for x in file_list if not exclude_dir or not any(z in os.path.dirname(x) for z in exclude_dir)]
    file_list = [x for x in file_list if not include_dir or any(z in os.path.dirname(x) for z in include_dir)]
    file_list = [x for x in file_list if not exclude_file or not any(z in os.path.basename(x) for z in exclude_file)]
    file_list = [x for x in file_list if not include_file or any(z in os.path.basename(x) for z in include_file)]
    return file_list

def remove_duplicates_by_filename(file_list: list) -> tuple[list, list]:
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

def filter_by_sheet_names(file_list: list) -> tuple:
    edms_bom_standard_list = []
    not_bom_file_list = []
    error_file_list = []
    sheet_names = ["Summary", "BOM", "Error", "Warning", "Status"]
    for path in file_list:
        try:
            xls = pd.ExcelFile(path, engine="xlrd")
            if all(i in xls.sheet_names for i in sheet_names):
                edms_bom_standard_list.append(path)
            else:
                not_bom_file_list.append(path)
        except:
            error_file_list.append(path)

    return edms_bom_standard_list, not_bom_file_list, error_file_list


if __name__=="__main__":
    root_dir = r"C:\Users\user\Vilesco\DATA_CORE - Документы\Z34\Z34 CDA HVAC MFZ 1-2\RAW\TUY\EDMS\TUSNA"
    include_file = ["xls"]
    exclude_file = []
    include_dir = []
    exclude_dir = ["_archive"]
    path_corrections_bom = ["BOM", "RPT", "BUM", "BOB", "RTP"] #


    file_list = get_file_list(root_dir)
    print("get_file_list")
    print(f"LEN file_list: {len(file_list)}\n")
    # for i in file_list:
    #     print(i)

    filter_by_folder_and_filename = filter_by_folder_and_filename(file_list, include_file, exclude_file, include_dir, exclude_dir)
    print("filter_by_folder_and_filename")
    print(f"LEN file_list: {len(filter_by_folder_and_filename)}\n")
    # for i in filter_by_folder_and_filename:
    #     print(i)

    remove_duplicates_by_filename, list_of_duplicates = remove_duplicates_by_filename(filter_by_folder_and_filename)
    print("remove_duplicates_by_filename")
    print(f"LEN file_list: {len(remove_duplicates_by_filename)}")
    if list_of_duplicates:
        print("Found duplicates")
        for i in list_of_duplicates:
            print(i)
    else:
        print("No duplicates")
    print("")





    bom_file_list,not_bom_file_list,error_file_list = filter_by_sheet_names(remove_duplicates_by_filename)
    print("\nfilter_by_sheet_names")
    print(f"LEN file_list: {len(bom_file_list)}")
    print(f"LEN not bom list: {len(not_bom_file_list)}")
    print(f"LEN opening errors: {len(error_file_list)}")

    if bom_file_list:
        print("\nFile_list")
        for i in bom_file_list:
            print(i)
    else:
        print("\nNo files to display")

    if not_bom_file_list:
        print("\nWrong type of BOM (by sheets) or another Excel files")
        for i in not_bom_file_list:
            print(i)
    else:
        print("\nAll BOM ok")

    if error_file_list:
        print("\nError in opening file")
        for i in error_file_list:
            print(i)
    else:
        print("\nNo Opening Errors")