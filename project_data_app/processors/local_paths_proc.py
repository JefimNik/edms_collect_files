class LocalPathsService:
    def __init__(self, files, dfs, logger):
        self.files = files
        self.dfs = dfs
        self.logger = logger

    def run_local_files(self):
        print("\n<<PathsService start>>")
        # -------- GET FILE PATHS --------
        file_list = self.files.get_files()
        df_paths = self.dfs.os_file_paths_to_df(file_list)
        self.logger.update_log_df(df_paths, "01")
        print(f"01 os_file_paths: {len(df_paths)}")

        # -------- FILTER FILE PATHS --------
        steps = [
            (self.dfs.filter_by_folder, ["dir"], "02"),
            (self.dfs.filter_by_extension, ["filename"], "03"),
            (self.dfs.filter_by_filename, ["filename"], "04"),
            (self.dfs.remove_duplicates_by_filename, ["filename"], "05"),
            (self.dfs.filter_by_sheet_names, ["filename"], "06"),
        ]

        for func, cols, step_name in steps:
            df_paths = func(df_paths)
            self.logger.update_log_df(df_paths, step_name, cols)
            print(f"{step_name} {func.__name__}: {df_paths.shape[0]}")

        print("<<PathsService finished>>")

        return df_paths["filepath"].tolist()


if __name__ == "__main__":
    from project_data_app.operations.PathList import PathList
    from project_data_app.services.source_data_service import LocalFileSource
    from project_data_app.core.config import ConfigManager
    from project_data_app.services.steplogger_service import StepLogger

    # -------- INIT --------

    config = ConfigManager("../config", "config_01.yaml", "xls")
    files = LocalFileSource(config)
    dfs = PathList(config)
    logger = StepLogger()

    # -------- RUN --------
    s01_paths = LocalPathsService(files, dfs, logger).run_local_files()
    dfs.df_to_excel(logger.df, "steps", sheet_name="paths")

