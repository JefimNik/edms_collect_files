import os

from sqlalchemy import create_engine, inspect
import pandas as pd
from pathlib import Path





class DatabaseManager:
    def __init__(self, db_path, db_name):
        db_path = Path(db_path) / db_name
        self.engine = create_engine(f"sqlite:///{db_path}")

    def save_to_db(self, df, table_name):
        df.to_sql(table_name, self.engine, if_exists="replace", index=False)

    def read_from_db(self, table_name):
        return pd.read_sql(f'select * from "{table_name}"', self.engine)

    def db_table_list(self):
        inspector = inspect(self.engine)
        return inspector.get_table_names()



    def db_tables_to_excel(self, table_list, output_dir, file_name="db_review.xlsx", df_config=None):
        file_path = os.path.join(output_dir, file_name)
        with pd.ExcelWriter(file_path, mode="w", engine="openpyxl") as writer:
            if df_config is None:
                df_config = pd.DataFrame([["no config added"]])
            df_config.to_excel(writer, sheet_name="config", index=False)
            for i in table_list:
                df = pd.read_sql(f'select * from "{i}"', self.engine)
                df.to_excel(writer, sheet_name=i[:31], index=False)
