from services.FilesystemService import FilesystemService
from sources.LocalfilesSource import LocalFileSource
from services.ConfigManager import ConfigManager
from services.StepLoggerService import StepLogger
from pipelines.paths_pipeline import PathsPipeline

if __name__ == "__main__":
    # -------- INIT --------
    config = ConfigManager("config_01", "xls")
    source = LocalFileSource(config)
    files = FilesystemService(config)
    logger = StepLogger()

    paths_pipeline = PathsPipeline(source, logger, files)

    # -------- COLLECT --------
    file_list = source.get_files()
    df_paths = files.os_file_paths_to_df(file_list)
    logger.update_log_df(df_paths, "01")

    # -------- FILTER FILE PATHS --------
    steps = [
        (files.filter_by_folder, ["dir"], "02"),
        (files.filter_by_extension, ["filename"], "03"),
        (files.filter_by_filename, ["filename"], "04"),
        (files.remove_duplicates_by_filename, ["filename"], "05"),
        (files.filter_by_sheet_names, ["filename"], "06"),
    ]

    for func, cols, step_name in steps:
        df_paths = func(df_paths)
        logger.update_log_df(df_paths, step_name, cols)
        print(f"{step_name} {func.__name__}: {df_paths.shape[0]}")

    # -------- RESULT --------
    filtered_file_paths = df_paths["filepath"].tolist()
    files.df_to_excel(logger.df, "steps")



