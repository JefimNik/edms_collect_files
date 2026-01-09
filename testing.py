import os
import pandas as pd


# pip install --upgrade pandas==1.5.3 --prefer-binary
# pip install xlrd==1.2.0
# python -m pip install --upgrade pip setuptools wheel

path = r"C:\USERS\USER\VILESCO\DATA_CORE - ДОКУМЕНТЫ\Z34\Z34 CDA HVAC MFZ 1-2\RAW\TUY\EDMS\TUSNA\DOC0000231069,TUSNA441,E4\BOM_TUSNA441_E4.XLS"
df = pd.read_excel(path, sheet_name="BOM", header=3, engine="xlrd", dtype=str)

test1 = pd.ExcelFile(path, engine="xlrd")
print(test1.sheet_names)