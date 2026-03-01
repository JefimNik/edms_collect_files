from project_data_app.core.config import ConfigManager
from project_data_app.operations.Bom01 import AddBomColumns, FilterBom, LocationExtractor
from project_data_app.operations.PathList import PathList
from project_data_app.services.database_service import DatabaseManager
from project_data_app.services.excel_service import Excel
# from project_data_app.services.pdf_service import PDF
from project_data_app.services.source_data_service import LocalFileSource
from project_data_app.services.steplogger_service import StepLogger

from project_data_app.processors.LocalPathsCollector import LocalPathsCollector

from project_data_app.pipelines.Bom01_pipeline import Bom01Pipeline


class PipelineFactory:

    def __init__(self, config_folder, config_name, config_type):
        self.config = ConfigManager(config_folder, config_name, config_type)

    def build_bom_pipeline(self):
        files = LocalFileSource(self.config)
        paths = PathList(self.config)
        excel = Excel(self.config)
        db = DatabaseManager(self.config)
        logger = StepLogger()

        paths_collector = LocalPathsCollector(files,paths,logger)

        return Bom01Pipeline(config=self.config, files=files, paths=paths, excel=excel,
                             db=db, logger=logger, add_cols=AddBomColumns, filter_cols=FilterBom,
                             paths_collector= paths_collector, location_extractor=LocationExtractor)


