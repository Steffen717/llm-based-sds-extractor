"""
Dieses Skript verarbeitet Sicherheitsdatenblätter im PDF-Format:

1. Extrahiert die Abschnitte (3, 11, 12) aus jeder PDF in einem Ordner, 
   die zwischen definierten Wortpaaren liegen. Falls diese keine Ergebnisse liefern, 
   werden alternative Fallback-Wörter aus den Listen ausprobiert.
2. Erstellt ein pdf dokument welches alle extrahierten Abschnitte enthält.
3. Analysiert die extrahierten Teile mit jeweils zugeschnittenen GPT-Anfragen.
4. Speichert die Ergebnisse als strukturierte JSON-Dateien.
5. Führt die Einzelinformationen zu einer finalen JSON-Datei zusammen.
6. PDFs mit fehlgeschlagenen Extraktionen werden in einen Fehlerordner verschoben.
7. Für jede PDF wird im Ausgabeordner ein eigener Unterordner erstellt, 
   der alle zugehörigen extrahierten PDF-Dateien und JSON-Ergebnisse enthält.
8. Konvertiert die finale JSON-Datei in eine Excel-Tabelle.
"""


import os
import json
import shutil
from split_pdfs_and_save import extract_between_words
from combine_pdf import merge_pdfs
from extract_information_part_03 import analyze_safety_data_sheet3
from extract_information_part_11 import analyze_safety_data_sheet11
from extract_information_part_12 import analyze_safety_data_sheet12
from process_and_merge_jsons import process_json_data
from JSON_to_excel import json_to_excel

def create_empty_json(path):
    with open(path, 'w') as f:
        json.dump({}, f)

def extract_sections_from_folder(input_folder, output_folder, failed_folder):
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(failed_folder, exist_ok=True)

    for file_name in os.listdir(input_folder):
        if not file_name.lower().endswith('.pdf'):
            continue

        pdf_path = os.path.join(input_folder, file_name)
        base_name = os.path.splitext(file_name)[0]
        pdf_output_folder = os.path.join(output_folder, base_name)
        os.makedirs(pdf_output_folder, exist_ok=True)

        # Abschnitt 3
# Abschnitt 3
        success3 = extract_between_words(
            pdf_path,
            "ABSCHNITT 3: Zusammensetzung/Angaben zu Bestandteilen", "ABSCHNITT 4: Erste-Hilfe Maßnahmen",
            pdf_output_folder,
            [
                "ABSCHNITT 3: Zusammensetzung/Angaben zu Bestandteilen",
                "Angaben zu Bestandteilen",
                "3.2 Gemische",
                "SECTION 3",
                "ABSCHNITT3",
                "Zusammensetzung"
            ],
            [
                "ABSCHNITT 4: Erste-Hilfe Maßnahmen",
                "Erste-Hilfe-Maßnahmen",
                "ERSTE-HILFE-MASSNAHMEN",
                "ABSCHNITT4",
                "SECTION 4"
            ],
            "_Abschnitt_3_extracted.pdf"
        )

        # Abschnitt 11
        success11 = extract_between_words(
            pdf_path,
            "ABSCHNITT 11: Toxikologische Angaben", "ABSCHNITT 12: Umweltbezogene Angaben",
            pdf_output_folder,
            [
                "ABSCHNITT 11: Toxikologische Angaben",
                "11. ANGABEN ZUR TOXIKOLOGIE",
                "Toxikologische Eigenschaften",
                "ANGABEN ZUR TOXIKOLOGIE",
                "Toxikologische Angaben",
                "Abschnitt 11",
                "SECTION 11"
            ],
            [
                "ANGABEN ZUR ÖKOLOGIE",
                "Umweltbezogene Angaben",
                "ABSCHNITT12"
                "SECTION 12",
                "12.1"
            ],
            "_Abschnitt_11_extracted.pdf"
        )

        # Abschnitt 12
        success12 = extract_between_words(
            pdf_path,
            "ABSCHNITT 12: Umweltbezogene Angaben", "13. HINWEISE ZUR ENTSORGUNG",
            pdf_output_folder,
            [
                "12. ANGABEN ZUR ÖKOLOGIE",
                "Umweltbezogene Angaben",
                "Ökotoxische Wirkungen",
                "ANGABEN ZUR ÖKOLOGIE",
                "ABSCHNITT 12",
                "SECTION 12"
            ],
            [
                "13. HINWEISE ZUR ENTSORGUNG",
                "Hinweise zur Entsorgung",
                "Entsorgung von Produkt",
                "HINWEISE ZUR ENTSORGUNG",
                "Abschnitt 13"
                "SECTION 13"
            ],
            "_Abschnitt_12_extracted.pdf"
        )


        if not (success3 and success11 and success12):
            shutil.copy2(pdf_path, os.path.join(failed_folder, file_name))
            print(f"Fehlgeschlagen: {file_name} kopiert nach {failed_folder}")
            continue

        # Analyse der Abschnitte mit chat-gpt
        try:
            jsonpath3 = analyze_safety_data_sheet3(success3, pdf_output_folder)
        except Exception as e:
            print(f"Fehler bei Abschnitt 3 in {file_name}: {e}")
            jsonpath3 = os.path.join(pdf_output_folder, f"{base_name}_result3.json")
            create_empty_json(jsonpath3)

        try:
            jsonpath11 = analyze_safety_data_sheet11(success11, pdf_output_folder)
        except Exception as e:
            print(f"Fehler bei Abschnitt 11 in {file_name}: {e}")
            jsonpath11 = os.path.join(pdf_output_folder, f"{base_name}_result11.json")
            create_empty_json(jsonpath11)

        try:
            jsonpath12 = analyze_safety_data_sheet12(success12, pdf_output_folder)
        except Exception as e:
            print(f"Fehler bei Abschnitt 12 in {file_name}: {e}")
            jsonpath12 = os.path.join(pdf_output_folder, f"{base_name}_result12.json")
            create_empty_json(jsonpath12)
            
        try:
            merged_pdf_path = os.path.join(pdf_output_folder, f"dokument.pdf")
            merge_pdfs(
                [
                    success3,
                    success11,
                    success12
                ],
                merged_pdf_path
            )
            print(f"PDFs zusammengeführt: {merged_pdf_path}")
        except Exception as e:
            print(f"Fehler beim Zusammenführen der PDFs: {e}")

        # JSON-Dateien kombinieren
        final_json = os.path.join(pdf_output_folder, f"{base_name}_final.json")
        try:
            process_json_data(jsonpath3, jsonpath11, jsonpath12, final_json)
            print(f"Verarbeitung abgeschlossen: {file_name}")
        except Exception as e:
            print(f"Fehler beim Kombinieren: {e}")
            create_empty_json(final_json)
            
        excel_output_path = os.path.join(pdf_output_folder, f"Tabelle.xlsx")
        if os.path.exists(final_json):
            try:
                json_to_excel(final_json, excel_output_path)
                print(f"Excel erfolgreich erstellt: {excel_output_path}")
            except Exception as e:
                print(f"Fehler bei der Erstellung der Excel-Datei aus {final_json}: {e}")
        else:
            print(f"Keine finale JSON-Datei gefunden für: {base_name}")