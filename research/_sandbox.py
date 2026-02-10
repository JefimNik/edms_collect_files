import os
import pandas as pd
import yaml


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_filtered_files(root_dir, include_dir, exclude_dir, include_file, exclude_file, sheet_names, engine):
    files = []
    for folder_path, _, file_names in os.walk(root_dir):
        folder_upper = folder_path.upper()
        if exclude_dir and any(x.upper() in folder_upper for x in exclude_dir):
            continue
        if include_dir and not any(x.upper() in folder_upper for x in include_dir):
            continue

        for file in file_names:
            file_path = os.path.join(folder_path, file).upper()
            file_name = os.path.basename(file_path)

            if exclude_file and any(x.upper() in file_name for x in exclude_file):
                continue
            if include_file and not any(x.upper() in file_name for x in include_file):
                continue

            try:
                xls = pd.ExcelFile(file_path, engine=engine)
                if all(sheet in xls.sheet_names for sheet in sheet_names):
                    files.append(file_path)
            except Exception:
                continue

    return list(dict.fromkeys(files))  # remove duplicates by filename (keep first)


def collect_dataframe(file_paths, sheet_name_to_concat, header_row, engine):
    dfs = []
    for path in file_paths:
        try:
            df = pd.read_excel(path, sheet_name=sheet_name_to_concat, header=header_row, engine=engine)
            dfs.append(df)
        except Exception:
            continue

    if not dfs:
        return pd.DataFrame()
    return pd.concat(dfs, ignore_index=True)


if __name__ == "__main__":
    config = load_config("../app/config/_config_bom_type1.yaml")
    c = config["collect_data"]
    root_dir = config["path_data"]["root_dir"]
    output_dir = config["path_data"]["output_dir"]
    file_type = c["file_type"]

    filtered_files = get_filtered_files(
        root_dir=root_dir,
        include_dir=c["include_dir"],
        exclude_dir=c["exclude_dir"],
        include_file=c["include_file"],
        exclude_file=c["exclude_file"],
        sheet_names=c["sheet_names"],
        engine=c["engine"]
    )

    df = collect_dataframe(
        file_paths=filtered_files,
        sheet_name_to_concat=c["sheet_name_to_concat"],
        header_row=c["header_row"],
        engine=c["engine"]
    )

    if not df.empty:
        output_path = os.path.join(output_dir, f"{file_type}_excel_collected.xlsx")
        df.to_excel(output_path, index=False)
        print(f"✔ Exported to: {output_path}")
    else:
        print("⚠ No data collected.")
