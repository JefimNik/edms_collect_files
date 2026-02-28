import pandas as pd


class StepLogger:
    def __init__(self, index_col: str = "row_id"):
        self.df = pd.DataFrame()
        self.index_col = index_col

    def update_log_df(self, df: pd.DataFrame, step_name: str, columns: list = None):
        if self.df.empty:
            self.df = df.copy()
        else:
            df = df.copy()

            if columns is None:
                pass
            else:
                for i in columns:
                    i = i+step_name
                df = df[[self.index_col] + columns]

            self.df = self.df.merge(df, left_on=self.index_col, right_on=self.index_col, how="left", suffixes=("", f"_{step_name}"))
