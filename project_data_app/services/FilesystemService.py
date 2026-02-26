import pandas as pd


class FilesystemService:

    def __init__(self, config):
        self.include_dir = config.include_dir
        self.exclude_dir = config.exclude_dir
        self.include_file = config.include_file
        self.exclude_file = config.exclude_file
        self.sheet_names = config.sheet_names
        self.engine = config.engine

    def make_df_from_list(self, file_list, column_name = "filepath"):
        df = pd.DataFrame({column_name: file_list})

        df["filepath"] = df[column_name].str.replace("\\", "/").str.upper()
        df["dir"] = df[column_name].str.rsplit("/", n=1).str[0]
        df["filename"] = df[column_name].str.rsplit("/", n=1).str[1]

        df = df.reset_index().rename(columns={"index":"row_id"})

        return df

    def filter_by_folder(self, df, dir_name="dir"):
        include_dir = [x.upper() for x in self.include_dir]
        exclude_dir = [x.upper() for x in self.exclude_dir]

        df = df.copy()

        if include_dir:
            pattern = "|".join(include_dir)
            df = df[df[dir_name].str.contains(pattern, regex=True)]

        if exclude_dir:
            pattern = "|".join(exclude_dir)
            df = df[~df[dir_name].str.contains(pattern, regex=True)]

        return df

    def filter_by_filename(self):
        f_name = "filter_by_filename"

        include_file = [x.upper() for x in self.include_file]
        exclude_file = [x.upper() for x in self.exclude_file]

        df_temp = self.df_collect_steps[["index", "filter_by_folder", "file"]].copy()
        df_temp.columns = ["index", "filter_by_folder_temp", f_name]

        if include_file:
            pattern = "|".join(include_file)
            df_temp = df_temp[df_temp[f_name].str.contains(pattern, regex=True)]

        if exclude_file:
            pattern = "|".join(exclude_file)
            df_temp = df_temp[~df_temp[f_name].str.contains(pattern, regex=True)]

        self.df_collect_steps = self.df_collect_steps.merge(df_temp, left_on=["index", "dir"],
                                                            right_on=["index", "filter_by_folder_temp"],
                                                            how="left")
        self.df_collect_steps = self.df_collect_steps.drop(columns=["filter_by_folder_temp"])

        return f_name

    def remove_duplicates_by_filename(self):
        """
        find same file names and remove last paths from list
        return filtered and dropped paths lists
        """
        f_name = "remove_duplicates_by_filename"

        # --- dataframe ---
        df_temp = self.df_collect_steps[["index", "filter_by_filename"]].copy()
        df_temp.columns = ["index", f_name]
        df_temp = df_temp.drop_duplicates(subset=[f_name])
        self.df_collect_steps = self.df_collect_steps.merge(df_temp, left_on="index", right_on="index", how="left")

        return None

    def filter_by_sheet_names(self):
        """
        filter files by checking sheet names inside
        """
        f_name = "filter_by_sheet_names"

        df_temp = self.df_collect_steps[["index", "filter_by_folder", "remove_duplicates_by_filename"]].copy()
        df_temp.columns = ["index", "filter_by_folder_temp", f_name]

        mask_valid = pd.Series(False, index=df_temp.index)

        for id, row in df_temp.iterrows():
            folder_path = row["filter_by_folder_temp"]
            file_name = row[f_name]

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
