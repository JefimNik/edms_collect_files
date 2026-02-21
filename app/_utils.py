import yaml
import os
import pandas as pd
import json
from pypdf import PdfReader, PdfWriter
from pathlib import Path


def load_config(config_path):
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def print_list_data(file_list, output_dir=None, text=""):
    print(f"\n---{text}---")
    print(f"LEN list: {len(file_list)}")

    filepath = os.path.join(output_dir, "RawData_paths.txt")

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(f"\n---{text}---\n")
        f.write(f"LEN list: {len(file_list)}\n")
        for path in file_list:
            f.write(f"          {path}\n")


def config_to_df(config):
    output_dir = config["path_data"]["output_dir"]

    df_config = pd.json_normalize(config).T.reset_index()
    df_config.columns = ["full_key", "value"]

    df_config[["category", "subcategory"]] = (
        df_config["full_key"].str.split(".", n=1, expand=True)
    )

    df_config = df_config[["category", "subcategory", "value"]]

    # 🔥 ВАЖНО — преобразуем list/dict в JSON
    df_config["value"] = df_config["value"].apply(
        lambda x: json.dumps(x, ensure_ascii=False)
        if isinstance(x, (list, dict))
        else x
    )

    return output_dir, df_config


def merge_pdf(pdf_list, output_dir, filename="all_isometrics_z34_stg.pdf"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / filename

    writer = PdfWriter()

    for pdf_path in sorted(pdf_list):
        reader = PdfReader(pdf_path, strict=False)
        for page in reader.pages:
            writer.add_page(page)

    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path



import pdfplumber
from tqdm import tqdm

from pypdf import PdfReader, PdfWriter

def pdf_coordinates(pdf_path, output_dir, file_name="pdf_coordinates", start=None, end=None):

    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    txt_file = output_dir / f"{file_name}.txt"

    reader = PdfReader(pdf_path, strict=False)
    total_pages = len(reader.pages)

    # если не заданы — весь файл
    if start is None:
        start = 0
    if end is None or end > total_pages:
        end = total_pages

    # header
    with open(txt_file, "w", encoding="utf-8") as f:
        f.write("p_i;w_i;text;x0;x1;top;bottom;height\n")

    # extraction
    with pdfplumber.open(pdf_path) as pdf, \
            open(txt_file, "a", encoding="utf-8") as f:

        for p_i in tqdm(range(start, end), desc="Pages"):
            page = pdf.pages[p_i]
            words = page.extract_words(use_text_flow=True)

            for w_i, w in enumerate(words):
                f.write(
                    f'{p_i+1};{w_i};{w["text"]};'
                    f'{w["x0"]};{w["x1"]};'
                    f'{w["top"]};{w["bottom"]};'
                    f'{w["height"]}\n'
                )

    return txt_file