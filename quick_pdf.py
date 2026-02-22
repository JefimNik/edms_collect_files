import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path

# --- пути ---
csv_path = Path(r"D:\Vilesco\DATA_CORE - Documents\_TEMPORARY\split_pdf\merged.csv")
pdf_path = Path(r"D:\Vilesco\DATA_CORE - Documents\_TEMPORARY\all_isometrics_z34_stg.pdf")
output_path = Path(r"D:\Vilesco\DATA_CORE - Documents\_TEMPORARY\split_pdf\sorted_output.pdf")

# --- читаем CSV ---
df = pd.read_csv(csv_path, sep=";")

# если нужно удалить дубликаты по p_i
df = df.drop_duplicates(subset=["p_i"])

# сортировка если нужно (если CSV уже в нужном порядке — убрать)
# df = df.sort_values("p_i")

page_numbers = df["p_i"].astype(int).tolist()

# --- читаем PDF ---
reader = PdfReader(str(pdf_path))
writer = PdfWriter()

total_pages = len(reader.pages)

for p in page_numbers:
    index = p - 1  # PDF индексируется с 0
    if 0 <= index < total_pages:
        writer.add_page(reader.pages[index])
    else:
        print(f"Страница {p} вне диапазона")

# --- сохраняем ---
with open(output_path, "wb") as f:
    writer.write(f)

# --- создаём новый CSV с новой нумерацией ---

df_new = df.copy().reset_index(drop=True)

# новая нумерация страниц
df_new["new_p_i"] = df_new.index + 1

# если хочешь сохранить старый номер
df_new = df_new.rename(columns={"p_i": "old_p_i"})

# порядок колонок
df_new = df_new[["old_p_i", "new_p_i", "text"]]

new_csv_path = Path(r"D:\Vilesco\DATA_CORE - Documents\_TEMPORARY\split_pdf\sorted_pages.csv")
df_new.to_csv(new_csv_path, sep=";", index=False)

print("Новый CSV создан:", new_csv_path)

print("Готово:", output_path)