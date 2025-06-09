"""
Einfaches Skript zum Extrahieren von Text aus einer PDF-Datei mit PyMuPDF (fitz).
"""

import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    # PDF öffnen
    doc = fitz.open(pdf_path)
    text = ""

    # Alle Seiten durchgehen und Text extrahieren
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Seite laden
        text += page.get_text()         # Text der Seite hinzufügen

    return text