import fitz  # pymupdf

pdf_dateien = [
    r"C:\Users\Benutzer\Documents\Projekte\Beispiel\Seite_3.pdf",
    r"C:\Users\Benutzer\Documents\Projekte\Beispiel\Seite_11.pdf",
    r"C:\Users\Benutzer\Documents\Projekte\Beispiel\Seite_12.pdf"
]

output_pdf_pfad = r"C:\Users\Benutzer\Documents\Projekte\Beispiel\zusammengefuehrt.pdf"

output_pdf = fitz.open()

for pdf_datei in pdf_dateien:
    doc = fitz.open(pdf_datei)
    output_pdf.insert_pdf(doc)
    doc.close()

output_pdf.save(output_pdf_pfad)
output_pdf.close()

