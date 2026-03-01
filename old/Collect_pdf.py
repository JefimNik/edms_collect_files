import pandas as pd

file_path = r"C:\Users\jniki\Desktop\itub_result\export_all.txt"
output_path = r"C:\Users\jniki\Desktop\result.xlsx"

# 1. Чтение
df = pd.read_csv(
    file_path,
    sep=";",
    engine="python",          # не C engine
    on_bad_lines="skip",      # пропустить кривые строки
    encoding="utf-8"
)

cols = ["x0", "top", "height"]
df[cols] = df[cols].apply(pd.to_numeric, errors="coerce")

# 2. Фильтры
text = df["text_spool"].fillna("")

df_spools = df[
    (df["x0"] > 550) &
    (df["top"] > 500) &
    (df["height"] > 11) &
    (df["height"] < 12.5) &
    text.str.len().between(9, 21) &
    ~text.str.contains(r"\+", regex=True) &
    ~text.str.contains("SUPP", case=False)
].copy()

df_pages = df[
    (df["x0"] > 700) &
    (df["top"] < 80) &
    (df["height"] > 14) &
    (df["height"] < 16)
].copy()

# 3. Merge
df_merged = df_spools.merge(
    df_pages,
    on="p_i",
    how="left",
    suffixes=("_spool", "_page")
)

# 4. Экспорт — writer открываем один раз
df_merged.to_csv(
    r"C:\Users\jniki\Desktop\merged.csv",
    sep=";",
    index=False
)

print("Done")