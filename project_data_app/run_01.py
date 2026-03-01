import pandas as pd

from operations.Dataframe import DataFrame
from operations.Sources import LocalFileSource
from operations.Config import ConfigManager
from services.steplogger_service import StepLogger
from services.paths_service import PathsService
from operations.Database import DatabaseManager
from services.bom_service import AddBomColumns, FilterBom

if __name__ == "__main__":
    # -------- INIT --------
    config = ConfigManager("config", "config_01", "xls")
    files = LocalFileSource(config)
    dfs = DataFrame(config)
    db = DatabaseManager(config)
    logger = StepLogger()

    # -------- RUN --------
    s01_paths = PathsService(files, dfs, logger).run()
    dfs.df_to_excel(logger.df, "steps", sheet_name="paths")
    db.save_to_db(logger.df, "paths")

    s02_raw_bom = files.collect_exel_to_df(s01_paths)
    db.save_to_db(s02_raw_bom, "raw_bom")
    dfs.df_to_excel(s02_raw_bom, file_name="steps", sheet_name="raw_bom")

    s03_bom_add_columns = AddBomColumns(s02_raw_bom).run()
    db.save_to_db(s03_bom_add_columns, "bom_add_cols")
    dfs.df_to_excel(s03_bom_add_columns, file_name="steps", sheet_name="added cols")

    s04_bom_filter = FilterBom(s03_bom_add_columns, config).run()
    db.save_to_db(s04_bom_filter, "bom_filter")
    dfs.df_to_excel(s04_bom_filter, file_name="steps", sheet_name="filtered")
    print(s04_bom_filter.shape)
