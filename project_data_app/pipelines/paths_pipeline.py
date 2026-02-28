class PathsPipeline:
    def __init__(self, source, logger, files):
        self.source = source
        self.files = files
        self.logger = logger

    def run(self):
        # -------- GET FILE PATHS --------
        file_list = self.source.get_files()
        df_paths = self.files.os_file_paths_to_df(file_list)
        self.logger.update_log_df(df_paths, "01")

        # -------- FILTER FILE PATHS --------
        steps = [
            (self.files.filter_by_folder, ["dir"], "02"),
            (self.files.filter_by_extension, ["filename"], "03"),
            (self.files.filter_by_filename, ["filename"], "04"),
            (self.files.remove_duplicates_by_filename, ["filename"], "05"),
            (self.files.filter_by_sheet_names, ["filename"], "06"),
        ]

        for func, cols, step_name in steps:
            df_paths = func(df_paths)
            self.logger.update_log_df(df_paths, step_name, cols)
            # print(f"{step_name} {func.__name__}: {df_paths.shape[0]}")

        return df_paths["filepath"].tolist()


if __name__ == "__main__":
    pass
