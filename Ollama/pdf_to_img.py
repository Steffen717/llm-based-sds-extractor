"""
Erstellt alle Seiten eines PDFs als Bilder und speichert sie in einem angegebenen Ordner.
"""

import fitz  # PyMuPDF
import os

def pdf_to_images(pdf_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    doc = fitz.open(pdf_path)

    image_paths = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=200)
        image_path = os.path.join(output_folder, f"page_{page_num + 1}.png")
        pix.save(image_path)
        image_paths.append(image_path)
        print(f"Seite {page_num + 1} als Bild gespeichert: {image_path}")

    return image_paths
