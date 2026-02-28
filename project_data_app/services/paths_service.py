class PathsService:
    def __init__(self, files, dfs, logger):
        self.source = files
        self.files = dfs
        self.logger = logger

    def run(self):
        print("\n<<PathsService start>>")
        # -------- GET FILE PATHS --------
        file_list = self.source.get_files()
        df_paths = self.files.os_file_paths_to_df(file_list)
        self.logger.update_log_df(df_paths, "01")
        print(f"01 os_file_paths: {len(df_paths)}")

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
            print(f"{step_name} {func.__name__}: {df_paths.shape[0]}")

        self.files.df_to_excel(self.logger.df, "s01_paths")
        print(f"\ns01_paths.xlsx created: {self.files.output_dir}")

        print("<<PathsService finished>>")

        return df_paths["filepath"].tolist()


if __name__ == "__main__":
    from project_data_app.operations.Dataframe import DataFrame
    from project_data_app.operations.Sources import LocalFileSource
    from project_data_app.operations.Config import ConfigManager
    from project_data_app.services.steplogger_service import StepLogger

    # -------- INIT --------

    config = ConfigManager("../config", "config_01.yaml", "xls")
    source = LocalFileSource(config)
    files = DataFrame(config)
    logger = StepLogger()

    # -------- RUN --------
    s01_paths = PathsService(source, logger, files)
    s01_paths.run()
