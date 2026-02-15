import sqlite3
import pandas as pd

class Tracker:
    def __init__(self):
        self.df = pd.DataFrame()
        return

    def add_column(self, column_name, values):
        self.df[column_name] = values
        return self.df


