import os
import pandas as pd
import yaml

from services.FilesystemService import FilesystemService
from sources.LocalfilesSource import LocalFileSource
from services.ConfigManager import ConfigManager
from services.StepLoggerService import StepLogger

if __name__ == "__main__":
    # fabric
    config = ConfigManager("config_01", "xls")
    source = LocalFileSource(config)
    files = FilesystemService(config)
    logger = StepLogger()

    # pipeline to transform and  filter file list
    file_list = source.get_files()

    df = files.os_file_paths_to_df(file_list)
    logger.update_log_df(df, "01")

    steps = [
        (files.filter_by_folder, ["dir"], "02"),
        (files.filter_by_extension, ["filename"], "03"),
        (files.filter_by_filename, ["filename"], "04"),
        (files.remove_duplicates_by_filename, ["filename"], "05"),
        (files.filter_by_sheet_names, ["filename"], "06"),
    ]

    for func, cols, step_name in steps:
        df = func(df)
        logger.update_log_df(df, step_name, cols)
        print(f"{func.__name__}: {df.shape[0]}")

    files.df_to_excel(logger.df, "steps")
