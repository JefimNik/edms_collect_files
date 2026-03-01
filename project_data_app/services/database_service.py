import os

from sqlalchemy import create_engine, inspect
import pandas as pd
from pathlib import Path


class DatabaseManager:
    def __init__(self, config):
        self.db_path = config.output_dir
        self.db_name = config.project_db
        self.db_full_path = Path(self.db_path) / self.db_name
        self.engine = create_engine(f"sqlite:///{self.db_full_path}")

    def save_to_db(self, df, table_name):
        df.to_sql(table_name, self.engine, if_exists="replace", index=False)

    def read_from_db(self, table_name):
        return pd.read_sql(f'select * from "{table_name}"', self.engine)

    def db_table_list(self):
        inspector = inspect(self.engine)
        return inspector.get_table_names()

    def db_tables_to_excel(self, table_list=None, output_dir=None, file_name="db_review.xlsx"):
        if table_list is None:
            inspector = inspect(self.engine)
            table_list =  inspector.get_table_names()

        if output_dir is None:
            output_dir = self.db_path

        file_path = os.path.join(output_dir, file_name)

        with pd.ExcelWriter(file_path, mode="w", engine="openpyxl") as writer:
            # if df_config is None:
            #     df_config = pd.DataFrame([["no config added"]])
            # df_config.to_excel(writer, sheet_name="config", index=False)
            for i in table_list:
                df = pd.read_sql(f'select * from "{i}"', self.engine)
                df.to_excel(writer, sheet_name=i[:31], index=False)

if __name__ == "__main__":
    pass