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
    print(len(file_list))

    df_01 = files.os_file_paths_to_df(file_list)
    logger.update_log_df(df_01, "01")

    df_02 = files.filter_by_folder(df_01)
    logger.update_log_df(df_02, "02", ["dir"])

    df_03 = files.filter_by_extension(df_02)
    logger.update_log_df(df_03, "025", ["filename"])

    df_04 = files.filter_by_filename(df_03)
    logger.update_log_df(df_04, "03", ["filename"])

    df_05 = files.remove_duplicates_by_filename(df_04)
    logger.update_log_df(df_05, "04", ["filename"])

    df_06 = files.filter_by_sheet_names(df_05)
    logger.update_log_df(df_06, "05", ["filename"])

    print(f"os_file_paths_to_df {df_01.shape[0]}")
    print(f"filter_by_folder {df_02.shape[0]}")
    print(f"filter_by_extension {df_03.shape[0]}")
    print(f"filter_by_filename {df_04.shape[0]}")
    print(f"remove_duplicates_by_filename {df_05.shape[0]}")
    print(f"filter_by_sheet_names {df_06.shape[0]}")

    files.df_to_excel(logger.df, "steps")
