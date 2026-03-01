import pandas as pd
from pathlib import Path


class Excel:

    def __init__(self, config):

        self.output_dir = config.output_dir

    def df_to_excel(self, df, file_name, sheet_name):
        if df.empty:
            df = pd.DataFrame()

        df = df.fillna(" ")  # only for steps!
        output_path = Path(self.output_dir) / f"{file_name}.xlsx"

        if not output_path.exists():
            df.to_excel(output_path, sheet_name=sheet_name, index=False)
        else:
            with pd.ExcelWriter(
                    output_path,
                    engine="openpyxl",
                    mode="a",
                    if_sheet_exists="replace") as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
