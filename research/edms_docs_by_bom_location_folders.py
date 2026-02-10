import pandas as pd
from pathlib import Path
import shutil

# --- INPUT ---
excel_path = Path(
    r"C:\Users\user\Vilesco\DATA_CORE - Документы\Z34\Z34 CDA STG TUY MFZ 1\_clean\_Material list EDMS BOM 20250115 ILT+NO_ILT.xlsx"
)

sheet_name = "BOM_combine"

output_root = excel_path.parent / "_FOLDERS_BY_LOCATION"
output_root.mkdir(exist_ok=True)

# --- READ EXCEL ---
df = pd.read_excel(
    excel_path,
    sheet_name=sheet_name,
    usecols=["__FILEPATH__", "LOCATION"]
).dropna(subset=["__FILEPATH__", "LOCATION"])

# --- SOURCE FOLDER ---
df["SRC_FOLDER"] = df["__FILEPATH__"].apply(
    lambda x: Path(str(x)).parent
)

# --- REMOVE DUPLICATES ---
df_unique = df[["SRC_FOLDER", "LOCATION"]].drop_duplicates()

# --- COPY FOLDERS ---
for _, row in df_unique.iterrows():
    src_folder = row["SRC_FOLDER"]
    location = str(row["LOCATION"]).strip()
    dst_root = output_root / location
    dst_folder = dst_root / src_folder.name

    dst_root.mkdir(parents=True, exist_ok=True)

    if not src_folder.exists():
        print(f"NOT FOUND: {src_folder}")
        continue

    if dst_folder.exists():
        print(f"SKIP (already exists): {dst_folder}")
        continue

    shutil.copytree(src_folder, dst_folder)

print("Done.")
