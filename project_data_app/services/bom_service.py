import numpy as np
import pandas as pd


class AddBomColumns:
    """
    Adds derived columns to BOM dataframe.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    # -------------------------
    # PUBLIC
    # -------------------------

    def run(self) -> pd.DataFrame:
        self._replace_nulls()
        self._add_mfz()
        self._add_spec()
        self._add_montage_place()
        self._add_material_type()
        self._add_filetype()
        self._cast_types()
        return self.df

    # -------------------------
    # PRIVATE
    # -------------------------

    def _replace_nulls(self):
        cols = ["SPEC_CODE", "SPEC_NAME"]
        self.df[cols] = self.df[cols].fillna("")

    def _add_mfz(self):
        self.df["MFZ"] = self.df["LOT"].astype(str).str[-1]

    def _add_spec(self):
        self.df["SPEC_"] = (
                self.df["SPEC_CODE"].astype(str)
                + self.df["SPEC_NAME"].astype(str)
        )

    def _add_montage_place(self):
        self.df["MONTAGE_PLACE"] = np.where(
            self.df["FAB_TAG"].isna(),
            "SHIP",
            "PREFAB"
        )

    def _add_material_type(self):
        conditions = [
            self.df["SPEC_"].str.contains("A", na=False),
            self.df["SPEC_"].str.contains("C", na=False),
            self.df["SPEC_"].str.contains("Z", na=False),
            self.df["SPEC_"].str.contains("P", na=False),
            self.df["SPEC_"].str.contains("X", na=False),
        ]

        choices = [
            "ACIER",
            "CUPRUM",
            "GALVANIZED",
            "PLASTIC",
            "INOX",
        ]

        self.df["MATERIAL_TYPE1"] = np.select(
            conditions,
            choices,
            default="NO_DATA"
        )

    def _add_filetype(self):
        # Аналог 3 уровней split "\" в Power Query
        split_cols = (
            self.df["__FILEPATH__"]
            .astype(str)
            .str.split("\\", expand=True)
        )

        if split_cols.shape[1] >= 3:
            self.df["FILETYPE"] = split_cols.iloc[:, 2]
        else:
            self.df["FILETYPE"] = None

    def _cast_types(self):
        self.df = self.df.astype({
            "MFZ": "string",
            "SPEC_": "string",
            "MONTAGE_PLACE": "string",
            "MATERIAL_TYPE1": "string",
        })


class FilterBom:
    def __init__(self, df, config):
        self.df = df.copy()

        self.ship = config.ship
        self.mfz = config.mfz
        self.stage_bom = config.stage_bom
        self.system = config.system

    # -------------------------
    # PUBLIC
    # -------------------------

    def run(self) -> pd.DataFrame:
        self._filter_mfz()
        self._filter_stage_bom()
        self._filter_ship()
        self._filter_qpipe()
        self._filter_system()
        return self.df

    # -------------------------
    # PRIVATE
    # -------------------------

    def _filter_mfz(self):
        if self.mfz:
            self.df = self.df[self.df["MFZ"].isin(self.mfz)]

    def _filter_stage_bom(self):
        if self.stage_bom:
            self.df = self.df[self.df["EREC_STAGE"].isin(self.stage_bom)]

    def _filter_ship(self):
        if self.ship:
            self.df = self.df[self.df["SHIP"].isin(self.ship)]

    def _filter_qpipe(self):
        self.df = self.df[
            ~self.df["IDENT_CODE"].astype(str).str.contains("QPIPE", na=False)]

    def _filter_system(self):
        if self.system:
            self.df = self.df[self.df["FUNCTION"].isin(self.system)]
