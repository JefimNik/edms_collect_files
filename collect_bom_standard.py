import os

def list_all_files(root_dir: str) ->list:
    all_files = []

    include = ["xls"]
    include = [x.upper() for x in include]

    exclude = ["_archive"]
    exclude = [x.upper() for x in exclude]

    path_corrections_bom = ["BOM", "RPT", "BUM", "BOB", "RTP"]

    # get all paths from dir folder and lower characters ->list
    for folder_path, _, file_names in os.walk(root_dir):
        for file_name in file_names:
                full_path = os.path.join(folder_path, file_name).upper()
                all_files.append(full_path)

    def filter_fil
    # exclude old and archived folders from list / include excel files
    all_files[:] = [x for x in all_files if not any(z in x for z in exclude)]
    all_files[:] = [x for x in all_files if any(z in x for z in include)]


    for i in all_files:
        print(i)




if __name__=="__main__":
    root_dir = r"C:\Users\user\Vilesco\DATA_CORE - Документы\Z34\Z34 CDA HVAC MFZ 1-2\RAW\TUY\EDMS"
    list_all_files(root_dir)
