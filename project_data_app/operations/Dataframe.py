import pandas as pd
from pathlib import Path


class DataFrame:

    def __init__(self, config):

        self.output_dir = config.output_dir

        self.include_dir = config.include_dir
        self.exclude_dir = config.exclude_dir
        self.include_ext = config.include_ext
        self.exclude_ext = config.exclude_ext
        self.include_file = config.include_file
        self.exclude_file = config.exclude_file
        self.sheet_names = config.sheet_names
        self.engine = config.engine

    def os_file_paths_to_df(self, file_list):
        df = pd.DataFrame({"filepath": file_list})

        df = df.reset_index().rename(columns={"index": "row_id"})
        df["filepath"] = df["filepath"].str.replace("\\", "/").str.upper()
        df["dir"] = df["filepath"].str.rsplit("/", n=1).str[0]
        df["filename"] = df["filepath"].str.rsplit("/", n=1).str[1]

        return df

    def filter_by_folder(self, df):
        include_dir = [x.upper() for x in self.include_dir]
        exclude_dir = [x.upper() for x in self.exclude_dir]

        df = df.copy()

        if include_dir:
            pattern = "|".join(include_dir)
            df = df[df["dir"].str.contains(pattern, regex=True)]

        if exclude_dir:
            pattern = "|".join(exclude_dir)
            df = df[~df["dir"].str.contains(pattern, regex=True)]

        return df

    def filter_by_extension(self, df):
        df = df.copy()

        df["ext"] = df["filename"].str.split(".").str[-1].str.upper()
        if self.include_ext:
            df = df[df["ext"].isin([x.upper().lstrip(".") for x in self.include_ext])]

        if self.exclude_ext:
            df = df[~df["ext"].isin([x.upper().lstrip(".") for x in self.exclude_ext])]

        return df

    def filter_by_filename(self, df):
        include_file = [x.upper() for x in self.include_file]
        exclude_file = [x.upper() for x in self.exclude_file]

        df = df.copy()

        if include_file:
            pattern = "|".join(include_file)
            df = df[df["filename"].str.contains(pattern, regex=True)]

        if exclude_file:
            pattern = "|".join(exclude_file)
            df = df[~df["filename"].str.contains(pattern, regex=True)]
        return df

    def remove_duplicates_by_filename(self, df):
        df = df.copy()
        df = df.drop_duplicates(subset=["filename"])
        return df

    def filter_by_sheet_names(self, df):
        valid_paths = []

        for full_path in df["filepath"].dropna().unique():

            try:
                xls = pd.ExcelFile(full_path, engine=self.engine)

                if all(sheet in xls.sheet_names for sheet in self.sheet_names):
                    valid_paths.append(full_path)

            except Exception:
                continue

        df = df[df["filepath"].isin(valid_paths)]
        return df

    def df_to_excel(self, df, file_name):
        if df.empty:
            df = pd.DataFrame()

        df = df.fillna(" ")  # only for steps!
        output_path = Path(self.output_dir) / f"{file_name}.xlsx"
        df.to_excel(output_path, index=False)
