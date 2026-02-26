import yaml
from pathlib import Path


class ConfigManager:
    def __init__(self, config_name, config_section):
        # ---Class variables---
        self.config_folder = Path("../config")

        if not config_name.endswith(".yaml"):
            config_name = f"{config_name}.yaml"
        self.config_name = config_name

        self.config = self.load_config()  # load once

        self.section_name = config_section
        self.section = self.config.get(config_section, {}) or {}  # gpt

        # ---Paths from config---
        self.root_dir = self.config["path_data"]["root_dir"]
        self.output_dir = self.config["path_data"]["output_dir"]

        # ---Names from config---
        self.project_db = self.config["name_list"]["project_db"]

        # ---Config variables---
        self.file_type = self.section.get("file_type", "")
        self.include_file = self.section.get("include_file", [])
        self.exclude_file = self.section.get("exclude_file", [])
        self.include_dir = self.section.get("include_dir", [])
        self.exclude_dir = self.section.get("exclude_dir", [])
        self.sheet_names = self.section.get("sheet_names", [])
        self.sheet_name_to_concat = self.section.get("sheet_name_to_concat", [])
        self.header_row = self.section.get("header_row", None)
        self.engine = self.section.get("engine", None)

    def load_config(self):
        config_path = Path(self.config_folder) / self.config_name

        with open(config_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def show_config(self):
        return yaml.dump(self.config, sort_keys=False, allow_unicode=True)
    #  !show only paths and selected section


if __name__ == "__main__":
    cm = ConfigManager("config_01", "xls")
    print(cm.section_name)
    print(cm.show_config())
