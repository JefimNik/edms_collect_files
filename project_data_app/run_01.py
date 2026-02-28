import os
import pandas as pd
import yaml

from services.FilesystemService import FilesystemService
from sources.LocalfilesSource import LocalFileSource
from services.ConfigManager import ConfigManager

if __name__ == "__main__":

    # fabric
    config = ConfigManager("config_01", "xls")
    source = LocalFileSource(config)
    files = FilesystemService(config)
    logger =

    # pipeline to transform and  filter file list
    file_list = source.get_files()

    df_01 = files.os_file_paths_to_df(file_list)
    df_02 = files.filter_by_folder(df_01)
    df_03 = files.filter_by_filename(df_02)
    df_04 = files.remove_duplicates_by_filename(df_03)





