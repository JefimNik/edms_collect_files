import pandas as pd
import re


class PlasticPrefab:
    def __init__(self, df):
        self.df = df
        self.valid_specs = {
            "P",
        }

        self.spec_connection_map = {
            "3P2090": "Polypropylene (PP-R)",
            "3P2130": "Polybutylene (PB) Multi-layer",
            "3P3230": "PVC",
            "3P3300": "Polyethylene (PE)",
            "3P3320": "Polyethylene (PE) Multi-layer",
            "3P8410": "PVC",
            "3P3210": "PVC",
            "3P8110": "PVC",
            "3P8450": "Polyethylene (PE)",
            "3P3316": "Polyethylene (PE)",
            "3P8150": "Polyethylene (PE)",
            "3P8151": "Polyethylene (PE)",
            "3P8515": "Polyethylene (PE)",
            "3P3370": "Polyethylene (PE) Multi-layer",
        }

    # ==========================================================
    # PUBLIC
    # ==========================================================

    # def run(self):
    #
    #     df = self._filter_base(self.df)
    #     df = self._group(df)
    #     df = self._format_output(df)
    #
    #     return df

    def run(self):

        df = self._filter_base(self.df)
        print("After filter:", df.shape)

        df = self._group(df)
        print("After group:", df.shape)

        df = self._format_output(df)
        print("After format:", df.shape)

        return df
    # ==========================================================
    # STEPS
    # ==========================================================

    def _filter_base(self, df: pd.DataFrame) -> pd.DataFrame:

        df = df[["FUNCTION", "INPUT1", "FAB_TAG", "SPEC_"]].copy()

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

        return df

    # ----------------------------------------------------------

    def _group(self, df: pd.DataFrame) -> pd.DataFrame:

        grouped = (
            df.groupby(["SPEC_", "FAB_TAG"])
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

        # filter ifit
        df = df[
            (df["DN_MIN"] > 25) |
            ((df["DN_MIN"] <= 25) &
             df["Connections"].str.contains("Multi-layer", na=False))
            ]

        # CATEGORY
        df["CATEGORY"] = df["Connections"]

        # Rename
        df = df.rename(columns={"FAB_TAG": "SPOOL"})

        # Sort like Power Query
        df = df.sort_values(
            by=["CATEGORY", "DN_MIN", "SPOOL"],
            ascending=[False, True, True],
        )

        # Remove helper columns
        df = df.drop(columns=["SPEC_", "DN_MIN"])

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
