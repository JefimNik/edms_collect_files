import pandas as pd
import re


class PrefabSpoolBuilder:
    def __init__(self, df):
        self.df = df
        self.valid_specs = {
            "A",
            "Z",
        }

        # self.valid_connections = valid_connections or {
        #     "Grooved coupling",
        #     "Welded",
        #     "Welded / Screwed",
        # }
        self.spec_connection_map = {
            "3A2391": "Grooved coupling",
            "2A5610": "Welded",
            "2A9010": "Welded",
            "3A9110": "Welded",
            "2A2430": "Welded",
            "3A2310": "Welded",
            "3A2420": "Welded",
            "3Z6050": "Welded",
            "1A5020": "Welded",
            "2A5020": "Welded",
            "3A5310": "Welded",
            "3A4310": "Welded",
            "3A4390": "Grooved coupling",
            "3A7030": "Welded",
            "3A0116": "Welded",
            "3Z8227": "Welded",
            "2Z8420": "Welded",
            "3A4130": "Welded",
            "3Z3320": "Welded",
            "3Z8030": "Welded",
            "3Z3310": "Welded",
            "3A8620": "Welded",
            "2A7420": "Welded",
            "1A4910": "Welded",
            "2A4010": "Welded",
            "3Z3330": "Welded",
            "3Z3390": "Grooved coupling",
            "3Z3392": "Grooved coupling",
            "3Z3395": "Grooved coupling",
            "3Z3397": "Grooved coupling",
            "3Z3497": "Grooved coupling",
            "2A6110": "Welded",
            "3A2810": "Welded",
            "3Z3510": "Welded",
            "3Z3391": "Grooved coupling",
            "3Z3396": "Grooved coupling",
            "3A3330": "Welded",
            "3A3010": "Welded",
            "3A2520": "Welded",
            "3A7040": "Welded",
            "3Z7040": "Welded",
            "3Z7116": "Welded",
            "3Z7130": "Welded",
            "3A2530": "Welded",
            "2A1030": "Welded",
            "2A1210": "Welded",
            "3A1010": "Welded",
            "3A2730": "Welded",
        }

    # ==========================================================
    # PUBLIC
    # ==========================================================

    def run(self):

        df = self._filter_base(self.df)
        df = self._group(df)
        df = self._format_output(df)

        return df

    # ==========================================================
    # STEPS
    # ==========================================================

    def _filter_base(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df[["FUNCTION", "INPUT1", "FAB_TAG", "SPEC_"]].copy()

        # SYSTEM column
        df["SYSTEM"] = df["FUNCTION"].apply(
            lambda x: "ILT" if x == "ILT" else "OTHER"
        )

        # -------- PARTIAL SPEC FILTER --------
        if self.valid_specs:
            pattern = "|".join(map(re.escape, self.valid_specs))
            df = df[
                df["SPEC_"]
                .astype(str)
                .str.contains(pattern, regex=True, na=False)
            ]

        # FAB_TAG must exist
        df = df[df["FAB_TAG"].notna() & (df["FAB_TAG"] != "")]

        # Spec filter
        # if self.valid_piping_specs:
        #     df = df[df["SPEC_"].isin(self.valid_piping_specs)]

        return df

    # ----------------------------------------------------------

    def _group(self, df: pd.DataFrame) -> pd.DataFrame:

        grouped = (
            df.groupby(["SPEC_", "SYSTEM", "FAB_TAG"])
            .agg(
                DN_MIN=("INPUT1", "min"),
                DN=("INPUT1", lambda x: " ".join(
                    map(str, sorted(set(x.dropna().astype(int))))
                ))
            )
            .reset_index()
        )

        return grouped

    # ----------------------------------------------------------

    def _format_output(self, df: pd.DataFrame) -> pd.DataFrame:

        # Add connections
        df["Connections"] = df["SPEC_"].map(self.spec_connection_map)

        # CATEGORY
        df["CATEGORY"] = df["Connections"] + " " + df["SYSTEM"]

        # Rename
        df = df.rename(columns={"FAB_TAG": "SPOOL"})

        # Sort like Power Query
        df = df.sort_values(
            by=["CATEGORY", "DN_MIN", "SPOOL"],
            ascending=[False, True, True],
        )

        # Remove helper columns
        df = df.drop(columns=["SPEC_", "SYSTEM", "DN_MIN"])

        # Trim DN
        df["DN"] = df["DN"].astype(str).str.strip()

        # Add production workflow columns
        workflow_cols = [
            "COMMENT PREFAB",
            "COMMENT MATERIAL",
            "S PREP",
            "CUT",
            "GROOVE",
            "LABEL",
            "F PREP",
            "S WELD",
            "F WELD",
            "DATE TO GALVA",
            "DATE FROM GALVA",
            "S VICTAULIC",
            "F VICTAULIC",
            "FINAL DELIVERY",
            "MONTAGE STATUS",
            "LOCATION",
        ]

        for col in workflow_cols:
            df[col] = ""

        # Final column order
        df = df[
            [
                "CATEGORY",
                "SPOOL",
                "DN",
                "COMMENT PREFAB",
                "COMMENT MATERIAL",
                "S PREP",
                "CUT",
                "GROOVE",
                "LABEL",
                "F PREP",
                "S WELD",
                "F WELD",
                "DATE TO GALVA",
                "DATE FROM GALVA",
                "S VICTAULIC",
                "F VICTAULIC",
                "FINAL DELIVERY",
                "MONTAGE STATUS",
                "LOCATION",
            ]
        ]

        return df