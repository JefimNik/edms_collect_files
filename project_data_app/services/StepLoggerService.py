import pandas as pd


class StepLogger:
    def __init__(self):
        self.df = pd.DataFrame()

    def create_log_df(self, df):
        self.df = df

    def update_log_df(self, df, step_name):
        df = df.copy()
        self.df = self.df.merge(df, left_on="row_id", right_on="row_id")
