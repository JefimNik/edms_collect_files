# from PyPDF2 import PdfReader, PdfWriter
# from reportlab.pdfgen import canvas
# from io import BytesIO
# from pathlib import Path
#
# pdf_path = Path(r"D:\Vilesco\DATA_CORE - Documents\_TEMPORARY\split_pdf\sorted_output.pdf")
# output_path = pdf_path.parent / "sorted_output_with_insert.pdf"
#
# text_to_add = "63 GROOVE ILT - 451-B-ILTZ1300-001 DN 20 - SPTUNEX0642B)"
#
# reader = PdfReader(str(pdf_path))
# writer = PdfWriter()
#
# # --- получаем размер 62 страницы ---
# page_62 = reader.pages[61]  # индекс 0-based
# width = float(page_62.mediabox.width)
# height = float(page_62.mediabox.height)
#
# # --- создаем страницу такого же размера ---
# packet = BytesIO()
# c = canvas.Canvas(packet, pagesize=(width, height))
#
# c.setFont("Helvetica", 16)
# text_width = c.stringWidth(text_to_add, "Helvetica", 16)
#
# # центрируем
# x = (width - text_width) / 2
# y = height / 2
#
# c.drawString(x, y, text_to_add)
# c.save()
#
# packet.seek(0)
# insert_pdf = PdfReader(packet)
#
# # --- копируем страницы и вставляем после 62 ---
# for i, page in enumerate(reader.pages, start=1):
#     writer.add_page(page)
#
#     if i == 62:
#         writer.add_page(insert_pdf.pages[0])
#
# with open(output_path, "wb") as f:
#     writer.write(f)
#
# print("Done")

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO
from pathlib import Path

pdf_path = Path(r"D:\Vilesco\DATA_CORE - Documents\_TEMPORARY\split_pdf\sorted_output.pdf")
output_path = pdf_path.parent / "sorted_output_final.pdf"

insert_text = "63 GROOVE ILT - 451-B-ILTZ1300-001 DN 20 - SPTUNEX0642B)"

reader = PdfReader(str(pdf_path))
writer = PdfWriter()

# --- размер 62 страницы ---
page_62 = reader.pages[61]
w62 = float(page_62.mediabox.width)
h62 = float(page_62.mediabox.height)

# --- создаем страницу-вставку ---
packet = BytesIO()
c = canvas.Canvas(packet, pagesize=(w62, h62))
c.setFont("Helvetica", 16)
text_width = c.stringWidth(insert_text, "Helvetica", 16)
c.drawString((w62 - text_width)/2, h62/2, insert_text)
c.save()

packet.seek(0)
insert_pdf = PdfReader(packet)

# --- копируем страницы и вставляем ---
for i, page in enumerate(reader.pages, start=1):
    writer.add_page(page)
    if i == 62:
        writer.add_page(insert_pdf.pages[0])

total_pages = len(writer.pages)

# --- корректная нумерация ---
for i in range(total_pages):
    page = writer.pages[i]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)

    packet = BytesIO()
    c = canvas.Canvas(packet, pagesize=(width, height))
    c.setFont("Helvetica", 9)

    number_text = f"{i+1} / {total_pages}"
    text_width = c.stringWidth(number_text, "Helvetica", 9)

    c.drawString((width - text_width)/2, 20, number_text)
    c.save()

    packet.seek(0)
    number_pdf = PdfReader(packet)
    page.merge_page(number_pdf.pages[0])

# --- сохранение ---
with open(output_path, "wb") as f:
    writer.write(f)

print("Done")