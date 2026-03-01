class Bom01Pipeline:

    def __init__(self,
                 config,
                 files,
                 paths,
                 excel,
                 db,
                 logger,
                 add_cols,
                 filter_cols):
        self.config = config
        self.files = files
        self.excel = excel
        self.db = db
        self.logger = logger
        self.paths = paths
        self.add_cols = add_cols
        self.filter_cols = filter_cols

    def run(self):
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
