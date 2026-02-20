from s01_RawData_collect_excel import RawData

class PdfOrganiser:
    def __init__(self, config):

        # --- Class variables---
        self.df_collect_steps = None
        self.df_combined_files = None

        # ---Paths from config---
        self.root_dir = config["path_data"]["root_dir"]
        self.output_dir = config["path_data"]["output_dir"]

        # --- config variables---
        self.file_type = config["collect_data"]["file_type"]
        self.include_file = config["collect_data"]["include_file"]
        self.exclude_file = config["collect_data"]["exclude_file"]
        self.include_dir = config["collect_data"]["include_dir"]
        self.exclude_dir = config["collect_data"]["exclude_dir"]
        self.engine = config["collect_data"]["engine"]



