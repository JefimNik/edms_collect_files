from operations.PathList import PathList
from project_data_app.services.source_data_service import LocalFileSource
from project_data_app.core.config import ConfigManager
from services.steplogger_service import StepLogger
from project_data_app.processors.LocalPathsCollector import LocalPathsCollector
from project_data_app.services.database_service import DatabaseManager
from project_data_app.operations.Bom01 import AddBomColumns, FilterBom
from project_data_app.services.excel_service import Excel

if __name__ == "__main__":
    # -------- INIT --------
    config = ConfigManager("config", "config_01", "xls")
    files = LocalFileSource(config)
    paths = PathList(config)
    excel = Excel(config)
    db = DatabaseManager(config)
    logger = StepLogger()

    # -------- RUN --------
    s01_paths = LocalPathsCollector(files, paths, logger).run_local_files()
    db.save_to_db(logger.df, "paths")
    excel.df_to_excel(logger.df, "steps", sheet_name="paths")

    s02_raw_bom = LocalFileSource(config).collect_exel_to_df(s01_paths)
    db.save_to_db(s02_raw_bom, "raw_bom")
    excel.df_to_excel(s02_raw_bom, file_name="steps", sheet_name="raw_bom")

    s03_bom_add_columns = AddBomColumns(s02_raw_bom).run()
    db.save_to_db(s03_bom_add_columns, "bom_add_cols")
    excel.df_to_excel(s03_bom_add_columns, file_name="steps", sheet_name="added cols")

    s04_bom_filter = FilterBom(s03_bom_add_columns, config).run()
    db.save_to_db(s04_bom_filter, "bom_filter")
    excel.df_to_excel(s04_bom_filter, file_name="steps", sheet_name="filtered")
