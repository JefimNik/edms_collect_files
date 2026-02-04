import pandas as pd
import os
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
from tqdm import tqdm

def apply_filter(df, column, values):
    if values is None:
        return df
    if isinstance(values, (list, tuple, set)) and len(values) == 0:
        return df
    return df[df[column].isin(values)]

def load_catalog_spool(excel_path):
    """
    Reads Catalog_spool table from Excel and returns:
    - df_catalog_spool
    - df_spool_list (from FAB_TAG)
    - df_isometrique_list (from ISOMETRIQUE)
    """
    material_type_filter = None
    mfz_filter = None # ["3"]
    function_filter = None # ["ILT"]
    spec_filter = None
    filetype_filter = None
    location_filter = None
    row_limit = None

    df_catalog_spool = pd.read_excel(
        excel_path,
        sheet_name="Catalog_spool"
    )

    df_catalog_spool = apply_filter(df_catalog_spool, "MATERIAL_TYPE1", material_type_filter)
    df_catalog_spool = apply_filter(df_catalog_spool, "MFZ", mfz_filter)
    df_catalog_spool = apply_filter(df_catalog_spool, "FUNCTION", function_filter)
    df_catalog_spool = apply_filter(df_catalog_spool, "SPEC_", spec_filter)
    df_catalog_spool = apply_filter(df_catalog_spool, "FILETYPE", filetype_filter)
    df_catalog_spool = apply_filter(df_catalog_spool, "LOCATION", location_filter)
    if row_limit:
        df_catalog_spool = df_catalog_spool.head(row_limit)



    df_spool_list = (
        df_catalog_spool[["FAB_TAG"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )

    df_isometrique_list = (
        df_catalog_spool[["ISOMETRIQUE"]]
        .dropna()
        .drop_duplicates()
        .reset_index(drop=True)
    )



    return df_catalog_spool, df_spool_list, df_isometrique_list



def collect_pdf_paths(root_dir):
    """
    Walk through root_dir and subfolders,
    collect all PDF file paths except those containing '(STAMP)' (case-insensitive).
    Returns: pdf_path_list
    """
    pdf_path_list = []
    seen_filenames = set()

    for root, _, files in os.walk(root_dir):
        for fname in files:
            fname_lower = fname.lower()

            if not fname_lower.endswith(".pdf"):
                continue
            if "stamped" in fname_lower:
                continue
            if "support" in fname_lower:
                continue
            if fname_lower in seen_filenames:
                continue

            full_path = os.path.join(root, fname)
            pdf_path_list.append(full_path)
            seen_filenames.add(fname_lower)

    return pdf_path_list



def merge_pdfs(pdf_path_list, output_pdf_path):
    """
    Merge list of PDF files into a single PDF.
    Order is preserved as in pdf_path_list.
    """
    merger = PdfMerger()

    for pdf_path in pdf_path_list:
        merger.append(pdf_path)
        print(pdf_path)

    with open(output_pdf_path, "wb") as f:
        merger.write(f)

    merger.close()

# def filtered_pdf(input_pdf_path, output_pdf_path, df_spool_list):
#     """
#     Create a new PDF containing only pages where
#     at least one FAB_TAG from df_spool_list is mentioned.
#     """
#     reader = PdfReader(input_pdf_path)
#     writer = PdfWriter()
#
#     # prepare normalized spool list once
#     spool_list_norm = [
#         str(spool).replace(" ", "").upper()
#         for spool in df_spool_list["FAB_TAG"]
#     ]
#
#     for page_index, page in enumerate(
#             tqdm(reader.pages, total=len(reader.pages), desc="Scanning PDF pages")
#     ):
#         try:
#             page_text = page.extract_text() or ""
#         except Exception:
#             continue
#
#         page_text_norm = page_text.replace(" ", "").upper()
#
#         for spool_norm in spool_list_norm:
#             if spool_norm in page_text_norm:
#                 writer.add_page(page)
#                 break  # page already accepted, go to next page
#
#     with open(output_pdf_path, "wb") as f:
#         writer.write(f)






# --- initial load ---

def filtered_pdf(input_pdf_path, output_pdf_path, df_spool_list):
    """
    Create a new PDF containing only pages where
    at least one FAB_TAG from df_spool_list is mentioned,
    excluding pages containing 'INDUS'.

    Adds column 'PDF_PAGE' to df_spool_list with page numbers
    referring to the NEW filtered PDF.
    Saves df_spool_list to 'spool_list.xlsx'.
    """
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    # normalize spool list once
    spool_list_raw = df_spool_list["FAB_TAG"].astype(str).tolist()
    spool_list_norm = [s.replace(" ", "").upper() for s in spool_list_raw]

    # container for page mapping (new pdf pages)
    spool_pages = {spool: [] for spool in spool_list_raw}

    new_pdf_page_index = 0  # 1-based numbering will be applied when saving

    for page in tqdm(reader.pages, total=len(reader.pages), desc="Scanning PDF pages"):
        try:
            page_text = page.extract_text() or ""
        except Exception:
            continue

        page_text_norm = page_text.replace(" ", "").upper()

        # hard stop filter
        # if "ORDRE" in page_text_norm:
        #     continue

        page_has_spool = False

        for spool_norm, spool_raw in zip(spool_list_norm, spool_list_raw):
            if spool_norm and spool_norm in page_text_norm:
                spool_pages[spool_raw].append(str(new_pdf_page_index + 1))
                page_has_spool = True

        if page_has_spool:
            writer.add_page(page)
            new_pdf_page_index += 1

    # write filtered PDF
    with open(output_pdf_path, "wb") as f:
        writer.write(f)

    # write page info back to dataframe
    df_spool_list["PDF_PAGE"] = df_spool_list["FAB_TAG"].apply(
        lambda x: ",".join(spool_pages.get(str(x), []))
    )

    # save excel
    df_spool_list.to_excel("spool_list_GALVANIZED.xlsx", index=False)

    return df_spool_list

EXCEL_PATH = r"C:\Users\user\Vilesco\DATA_CORE - Документы\V35\V35 CDA STG TUY MFZ 4-5\_clean files\Material list EDMS BOM 2026-02-03 - GALVANIZED.xlsx"
# --- pdf paths ---
PDF_ROOT_DIR = r"C:\Users\user\Vilesco\DATA_CORE - Документы\V35\V35 CDA STG TUY MFZ 4-5\EDMS_RAW_N34"
# --- merge all PDFs ---
# OUTPUT_PDF_PATH = r"C:\Users\user\Vilesco\DATA_CORE - Документы\V35\V35 CDA STG TUY MFZ 4-5\merged_all.pdf"
# OUTPUT_FILTERED_PDF_PATH = r"C:\Users\user\Vilesco\DATA_CORE - Документы\V35\V35 CDA STG TUY MFZ 4-5\merged_filtered.pdf"

OUTPUT_PDF_PATH = r"C:\Users\user\Vilesco\DATA_CORE - Документы\V35\V35 CDA STG TUY MFZ 4-5\merged_filtered.pdf"
OUTPUT_FILTERED_PDF_PATH = r"C:\Users\user\Vilesco\DATA_CORE - Документы\V35\V35 CDA STG TUY MFZ 4-5\merged_filtered_GALVANIZED.pdf"
# --- filters (None or empty = no filter) ---



df_catalog_spool, df_spool_list, df_isometrique_list = load_catalog_spool(EXCEL_PATH)
print(len(df_catalog_spool))
#pdf_path_list = collect_pdf_paths(PDF_ROOT_DIR)
#merge_pdfs(pdf_path_list, OUTPUT_PDF_PATH) # all isometric from filtered bom
filtered_pdf(OUTPUT_PDF_PATH, OUTPUT_FILTERED_PDF_PATH, df_spool_list)
