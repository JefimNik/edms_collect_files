from operations.Dataframe import DataFrame
from operations.Sources import LocalFileSource
from operations.Config import ConfigManager
from services.steplogger_service import StepLogger
from services.paths_service import PathsService

if __name__ == "__main__":

    # -------- INIT --------
    config = ConfigManager("config", "config_01", "xls")
    files = LocalFileSource(config)
    dfs = DataFrame(config)
    logger = StepLogger()

    # -------- RUN --------
    s01_paths = PathsService(files, dfs, logger).run()
    s02_full_bom = files.collect_exel_to_df(s01_paths)
    dfs.df_to_excel(s02_full_bom, file_name="collected_bom")

