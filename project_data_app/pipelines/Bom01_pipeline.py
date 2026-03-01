from typing import TYPE_CHECKING, Type

if TYPE_CHECKING:
    from project_data_app.services.database_service import DatabaseManager
    from project_data_app.services.excel_service import Excel
    from project_data_app.operations.PathList import PathList
    from project_data_app.services.source_data_service import LocalFileSource
    from project_data_app.services.steplogger_service import StepLogger
    from project_data_app.processors.LocalPathsCollector import LocalPathsCollector
    from project_data_app.core.config import ConfigManager
    from project_data_app.operations.Bom01 import AddBomColumns, FilterBom


class Bom01Pipeline:

    def __init__(self,
                 config: ConfigManager,
                 files: LocalFileSource,
                 paths: PathList,
                 excel: Excel,
                 db: DatabaseManager,
                 logger: StepLogger,
                 add_cols: Type[AddBomColumns],
                 filter_cols: Type[FilterBom],
                 paths_collector: LocalPathsCollector,
                 location_extractor
    ):
        self.config = config
        self.files = files
        self.excel = excel
        self.db = db
        self.logger = logger
        self.paths = paths
        self.add_cols = add_cols
        self.filter_cols = filter_cols

        self.paths_collector = paths_collector
        self.location_extractor = location_extractor

    def run(self):
        s01_paths = self.paths_collector.run_local_files()
        self.db.save_to_db(self.logger.df, "paths")
        self.excel.df_to_excel(self.logger.df, "steps", sheet_name="paths")

        s02_raw_bom = self.files.collect_exel_to_df(s01_paths)
        self.db.save_to_db(s02_raw_bom, "raw_bom")
        self.excel.df_to_excel(s02_raw_bom, file_name="steps", sheet_name="raw_bom")

        s03_bom_add_columns = self.add_cols(s02_raw_bom).run()
        self.db.save_to_db(s03_bom_add_columns, "bom_add_cols")
        self.excel.df_to_excel(s03_bom_add_columns, file_name="steps", sheet_name="added cols")

        s04_bom_filter = self.filter_cols(s03_bom_add_columns, self.config).run()
        self.db.save_to_db(s04_bom_filter, "bom_filter")
        self.excel.df_to_excel(s04_bom_filter, file_name="steps", sheet_name="filtered")

        s05_bom_locations = self.location_extractor(s04_bom_filter).run()
        self.db.save_to_db(s05_bom_locations, "bom_locations")
        self.excel.df_to_excel(s05_bom_locations, file_name="steps", sheet_name="bom_locations")