"""
Dieses Skript kombiniert mehrere PDF-Dateien zu einer einzigen PDF-Datei.
"""

import fitz
import os

def merge_pdfs(pdf_dateien, output_pdf_pfad):
    output_pdf = fitz.open()

    for pdf_datei in pdf_dateien:
        if not os.path.isfile(pdf_datei):
            print(f"Datei nicht gefunden: {pdf_datei}")
            continue
        try:
            doc = fitz.open(pdf_datei)
            output_pdf.insert_pdf(doc)
            doc.close()
        except Exception as e:
            print(f"Fehler bei {pdf_datei}: {e}")

    os.makedirs(os.path.dirname(output_pdf_pfad), exist_ok=True)
    output_pdf.save(output_pdf_pfad)
    output_pdf.close()
    print(f"Gespeichert: {output_pdf_pfad}")

