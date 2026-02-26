import os
import pandas as pd
import yaml

from services.FilesystemService import FilesystemService
from sources.LocalfilesSource import LocalFileSource
from services.ConfigManager import ConfigManager


if __name__ == "__main__":
    config = ConfigManager("config_01", "xls")
    print(config.show_config())

    lfs = LocalFileSource(config)
    file_list = lfs.get_files()

    print(len(file_list))

    fc = FilesystemService(config)
    df = fc.make_df_from_list(file_list)

    print(df.info)


