from operations.Dataframe import DataFrame
from operations.Sources import LocalFileSource
from operations.Config import ConfigManager
from services.steplogger_service import StepLogger
from services.paths_service import PathsService
from operations.Database import DatabaseManager

if __name__ == "__main__":

    # -------- INIT --------
    config = ConfigManager("config", "config_01", "xls")
    files = LocalFileSource(config)
    dfs = DataFrame(config)
    db = DatabaseManager(config)
    logger = StepLogger()

    # -------- RUN --------
    s01_paths = PathsService(files, dfs, logger).run()

    s02_raw_bom = files.collect_exel_to_df(s01_paths)
    db.save_to_db(s02_raw_bom, "raw_bom")
    dfs.df_to_excel(s02_raw_bom, file_name="collected_bom")




