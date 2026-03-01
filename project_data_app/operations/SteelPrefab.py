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
        self.valid_piping_specs = {
            "3A2391",
            "3A4390",
            "3Z3390",
            "3Z3392",
            "3Z3395",
            "3Z3397",
            "3Z3497",
            "3Z3391",
            "3Z3396",
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

        # Connections filter
        if self.valid_piping_specs:
            df = df[df["SPEC_"].isin(self.valid_piping_specs)]

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

        # CATEGORY
        df["CATEGORY"] = df["SPEC_"] + " " + df["SYSTEM"]

        # # Replace naming
        # df["CATEGORY"] = df["CATEGORY"].replace(
        #     "Grooved coupling ILT",
        #     "GROOVE ILT"
        # )

        # Rename
        df = df.rename(columns={"FAB_TAG": "SPOOL"})

        # Sort like Power Query
        df = df.sort_values(
            by=["SPEC_", "SYSTEM", "DN_MIN", "SPOOL"],
            ascending=[False, True, True, True],
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