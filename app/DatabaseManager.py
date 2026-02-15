from sqlalchemy import create_engine, inspect
import pandas as pd
from pathlib import Path


class DatabaseManager:
    def __init__(self, db_path, db_name):
        db_path = Path(db_path)/ db_name
        self.engine = create_engine(f"sqlite:///{db_path}")

    def save_to_db(self, df, table_name):
        df.to_sql(table_name, self.engine, if_exists="replace", index=False)

    def read_from_db(self, table_name):
        return pd.read_sql(f"select * from {table_name}", self.engine)

    def db_table_list(self):
        inspector = inspect(self.engine)
        return inspector.get_table_names()
