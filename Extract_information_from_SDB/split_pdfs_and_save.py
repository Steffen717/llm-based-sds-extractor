"""
Dieses Skript durchsucht PDF-Dateien in einem Ordner nach einem Start- und einem Endwort.
Es extrahiert den Textbereich zwischen diesen beiden Wörtern (auch über mehrere Seiten hinweg)
und speichert diesen als neuen PDF-Ausschnitt in einem Ausgabeordner.
Wenn kein passender Bereich gefunden wird, wird die PDF-Datei in einen Fehlerordner kopiert.
"""

import os
import shutil
import fitz  # PyMuPDF

def extract_between_words_from_folder(input_folder, word1, word2, output_folder, failed_folder, fallback_words1=None, fallback_words2=None):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    if not os.path.exists(failed_folder):
        os.makedirs(failed_folder)

    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith('.pdf'):
            pdf_path = os.path.join(input_folder, file_name)
            success = extract_between_words(pdf_path, word1, word2, output_folder, fallback_words1, fallback_words2)
            if not success:
                failed_copy_path = os.path.join(failed_folder, file_name)
                shutil.copy2(pdf_path, failed_copy_path)
                print(f"Kopie gespeichert in: {failed_copy_path}")

def extract_between_words(pdf_path, word1, word2, output_folder, fallback_words1=None, fallback_words2=None, pdf_name=None):
    doc = fitz.open(pdf_path)
    fallback_words1 = fallback_words1 or []
    fallback_words2 = fallback_words2 or []

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    all_start_words = [word1] + fallback_words1
    all_end_words = [word2] + fallback_words2

    for start_word in all_start_words:
        for end_word in all_end_words:
            start_pos = None
            end_pos = None

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text").lower()

                if start_pos is None and start_word.lower() in text:
                    areas = page.search_for(start_word.lower())
                    if areas:
                        start_pos = (page_num, areas[0])

                if start_pos and end_pos is None and end_word.lower() in text:
                    areas = page.search_for(end_word.lower())
                    if areas:
                        end_pos = (page_num, areas[0])
                        break

            if start_pos and end_pos:
                output_file_name = f"{base_name}{pdf_name}"
                if start_pos[0] == end_pos[0]:
                    output_path = extract_from_same_page(doc, start_pos, end_pos, output_folder, output_file_name)
                else:
                    output_path = extract_from_different_pages(doc, start_pos, end_pos, output_folder, output_file_name)
                doc.close()
                return output_path

    doc.close()
    return None

def extract_from_same_page(doc, start_pos, end_pos, output_folder, output_file_name):
    new_doc = fitz.open()
    page = doc[start_pos[0]]
    clip = fitz.Rect(0, start_pos[1].y0, page.rect.width, end_pos[1].y0)
    new_page = new_doc.new_page(width=page.rect.width, height=clip.height)
    new_page.show_pdf_page(new_page.rect, doc, start_pos[0], clip=clip)
    output_path = os.path.join(output_folder, output_file_name)
    new_doc.save(output_path)
    new_doc.close()
    print(f"Gespeichert in {output_path}")
    return output_path

def extract_from_different_pages(doc, start_pos, end_pos, output_folder, output_file_name):
    new_doc = fitz.open()
    for page_num in range(start_pos[0], end_pos[0] + 1):
        page = doc[page_num]
        if page_num == start_pos[0]:
            clip = fitz.Rect(0, start_pos[1].y0, page.rect.width, page.rect.height)
        elif page_num == end_pos[0]:
            clip = fitz.Rect(0, 0, page.rect.width, end_pos[1].y0)
        else:
            clip = fitz.Rect(0, 0, page.rect.width, page.rect.height)
        new_page = new_doc.new_page(width=page.rect.width, height=clip.height)
        new_page.show_pdf_page(new_page.rect, doc, page_num, clip=clip)
    output_path = os.path.join(output_folder, output_file_name)
    new_doc.save(output_path)
    new_doc.close()
    print(f"Gespeichert in {output_path}")
    return output_path