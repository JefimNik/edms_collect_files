import numpy as np
import pandas as pd
import re


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


class LocationExtractor:
    def __init__(self, df, replacements=None):
        self.df = df.copy()
        self.replacements = replacements or [".", " ", "-"]

    # =========================
    # PUBLIC
    # =========================
    def run(self):

        df = self._prepare_base(self.df)
        df = self._split_tokens(df)
        df = self._classify(df)
        return self._final_cleanup(df)

    # =========================
    # INTERNAL STEPS
    # =========================

    def _prepare_base(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[["__FILENAME__", "LOT"]].copy()
        df["__FILENAME__"] = df["__FILENAME__"].astype(str)
        df["LOT"] = df["LOT"].astype(str)

        df["Merged"] = df["__FILENAME__"] + "_" + df["LOT"]
        df = df[["Merged"]].drop_duplicates()

        for ch in self.replacements:
            df["Merged"] = df["Merged"].str.replace(ch, "_", regex=False)

        return df

    def _split_tokens(self, df: pd.DataFrame) -> pd.DataFrame:
        # split by "_"
        df = df.assign(Merged=df["Merged"].str.split("_")).explode("Merged")
        df["Merged"] = df["Merged"].astype(str)

        # custom split (digits after position >=4)
        df["CustomSplit"] = df["Merged"].apply(self._custom_split)
        df = df.explode("CustomSplit")

        df = df[["CustomSplit"]].drop_duplicates()

        return df

    def _custom_split(self, txt: str):
        match = re.search(r"\d", txt)
        if match and match.start() >= 4:
            pos = match.start()
            return [txt[:pos], txt[pos:]]
        return [txt]

    def _classify(self, df: pd.DataFrame) -> pd.DataFrame:
        df["Category"] = df["CustomSplit"].apply(self._categorize)
        df = df[df["Category"] != "delete"]

        df = df.rename(columns={"CustomSplit": "Location"})
        return df

    def _categorize(self, val: str) -> str:
        val = str(val)
        length = len(val)

        first_char = val[:1]
        first_two = val[:2]
        first_three = val[:3]
        fourth_char = val[3:4] if length >= 4 else ""

        if first_char == "0":
            return "BLOCK"
        elif length == 3 and val.isdigit():
            return "LOT"
        elif (
                length >= 4
                and first_three.isdigit()
                and not fourth_char.isdigit()
        ):
            return "ACR"
        elif first_two == "99":
            return "VAT"
        elif length == 4 and val.isdigit() and first_two != "99":
            return "PANEL"
        else:
            return "delete"

    # def _merge_locations(
    #         self,
    #         df_main: pd.DataFrame,
    #         df_locations_t: pd.DataFrame,
    # ) -> pd.DataFrame:
    #
    #     df_combined = pd.concat([df_main, df_locations_t], ignore_index=True)
    #
    #     # приоритет новых сверху (как в PQ)
    #     df_combined["Index"] = range(1, len(df_combined) + 1)
    #     df_combined = df_combined.sort_values("Index", ascending=False)
    #
    #     df_combined = df_combined.drop_duplicates(subset=["Location"])
    #
    #     return df_combined

    def _final_cleanup(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df[["Location", "Category"]].copy()

        df = df.dropna(subset=["Location"])
        df = df[df["Location"] != ""]

        df["Location"] = df["Location"].astype(str)
        df["Category"] = df["Category"].astype(str)

        return df
