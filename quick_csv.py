import pandas as pd
import numpy as np


def read_source(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(
        file_path,
        sep=";",
        engine="python",
        on_bad_lines="skip",
        encoding="utf-8"
    )

    cols = ["x0", "top", "height"]
    df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")
    return df


def transform_spool(df: pd.DataFrame) -> pd.DataFrame:
    text = df["text"].fillna("")

    return df[
        (df["x0"] > 550) &
        (df["top"] > 500) &
        (df["height"].between(11, 12.5)) &
        text.str.len().between(9, 21) &
        ~text.str.contains(r"\+", regex=True) &
        ~text.str.contains("SUPP", case=False)
        ].copy()


def transform_pages(df: pd.DataFrame) -> pd.DataFrame:
    df = df[
        (df["x0"] > 1100) &
        (df["top"] < 80) &
        (df["height"].between(13, 15))
        ][["p_i", "text"]].copy()

    df["text"] = pd.to_numeric(df["text"], errors="coerce")
    df = df.sort_values(["p_i", "text"])
    df["text"] = df["text"].astype("Int64").astype("string")

    def process_group(series):
        result = []
        for s in series:
            if pd.isna(s):
                result.append("")
            elif len(s) == 4:
                result.extend([s[:2], s[2:]])
            else:
                result.append(s)
        return "/".join(result)

    grouped = (
        df.groupby("p_i")["text"]
        .apply(process_group)
        .reset_index(name="Custom")
    )

    grouped["Custom"] = grouped["Custom"].replace("", np.nan).ffill()

    split_cols = grouped["Custom"].str.split("/", expand=True)

    grouped["gr1"] = pd.to_numeric(split_cols[0], errors="coerce")
    grouped["gr2"] = pd.to_numeric(split_cols[1], errors="coerce")

    return grouped[["p_i", "Custom", "gr1", "gr2"]]


def merge_data(df_spools: pd.DataFrame, df_pages: pd.DataFrame) -> pd.DataFrame:
    df_merged = df_spools.merge(
        df_pages,
        on="p_i",
        how="left"
    )
    return df_merged


def df_clean(df_merged):
    df_cleaned = (
        df_merged[["p_i", "text"]]
        .drop_duplicates(subset=["p_i", "text"])
        .reset_index(drop=True)
    )
    return df_cleaned


def export_csv(df: pd.DataFrame, output_path: str):
    df.to_csv(output_path, sep=";", index=False)


# ================== RUN ==================

file_path = r"D:\Vilesco\DATA_CORE - Documents\_TEMPORARY\export_all.txt"
output_path = r"D:\Vilesco\DATA_CORE - Documents\_TEMPORARY\merged.csv"

df = read_source(file_path)
df_spools = transform_spool(df)
df_pages = transform_pages(df)
df_merged = merge_data(df_spools, df_pages)
df_cleaned = df_clean(df_merged)

export_csv(df_cleaned, output_path)

print("Done")
