import pandas as pd


class FilesystemService:

    def __init__(self, config):
        self.include_dir = config.include_dir
        self.exclude_dir = config.exclude_dir
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
        df = df.drop_duplicates(subset=["row_id"])
        return df

    def filter_by_sheet_names(self, df):
        df = df.copy()
        mask_valid = pd.Series(False, index=df.index)

        for id, row in df.iterrows():
            folder_path = row["dir"]
            file_name = row["filename"]
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

        self.df_collect_steps = self.df_collect_steps.merge(df_temp, left_on="index", right_on="index", how="left")
        # self.df_collect_steps = self.df_collect_steps[
        #     "index",
        #     "get_file_list",
        #     # "dir",
        #     "filter_by_folder",
        #     "file",
        #     "filter_by_filename",
        #     "remove_duplicates_by_filename",
        #     "filter_by_sheet_names",
        # ]

        return None
