from operations.Dataframe import DataFiles
from operations.Sources import LocalFileSource
from operations.Config import ConfigManager
from services.steplogger_service import StepLogger
from services.paths_service import PathsService

if __name__ == "__main__":

    # -------- INIT --------
    config = ConfigManager("config", "config_01", "xls")
    source = LocalFileSource(config)
    files = DataFiles(config)
    logger = StepLogger()

    # -------- RUN --------
    s01_paths = PathsService(source, logger, files)
    s01_paths.run()

