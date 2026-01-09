import os

def list_all_files(root_dir: str) ->list:
    all_files = []
    path_corrections_bom = ["BOM", "RPT", "BUM", "BOB", "RTP"]
    # get all paths from dir folder and lower characters ->list
    for folder_path, _, file_names in os.walk(root_dir):
        for file_name in file_names:
                full_path = os.path.join(folder_path, file_name).upper()
                all_files.append(full_path)

    return all_files # already upper

def filter_list_all_files(all_files: list, include, exclude) -> list:
    include = [x.upper() for x in include]
    exclude = [x.upper() for x in exclude]
    # exclude old and archived folders from list / include only excel files / remove duplicates by file name
    all_files= [x for x in all_files if not any(z in os.path.dirname(x) for z in exclude)]
    all_files= [x for x in all_files if any(z in os.path.basename(x) for z in include)]
    return all_files

def remove_duplicates(all_files: list) -> tuple[list, list]:
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





if __name__=="__main__":
    root_dir = r"C:\Users\user\Vilesco\DATA_CORE - Документы\Z34\Z34 CDA HVAC MFZ 1-2\RAW\TUY\EDMS"

    include = ["xls"]
    exclude = ["_archive"]


    all_files = list_all_files(root_dir)
    print(f"LEN all_files: {len(all_files)}")

    all_files = filter_list_all_files(all_files, include, exclude)
    print(f"LEN all_files after include/ex: {len(all_files)}")

    all_files, duplicates = remove_duplicates(all_files)
    print(f"LEN all_files after remove duplicates in file names: {len(all_files)}")

    if duplicates:
        print("Found duplicates")
        for i in duplicates:
            print(i)
    else:
        print("No duplicates")