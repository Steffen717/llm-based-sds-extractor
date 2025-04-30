"""
Dieses Skript verarbeitet Sicherheitsdatenblätter im PDF-Format:

1. Extrahiert die Abschnitte (3, 11, 12) aus jeder PDF in einem Ordner, 
   die zwischen definierten Wortpaaren liegen. Falls diese keine Ergebnisse liefern, 
   werden alternative Fallback-Wörter aus den Listen ausprobiert.
2. Analysiert die extrahierten Teile mit jeweils zugeschnittenen GPT-Anfragen.
3. Speichert die Ergebnisse als strukturierte JSON-Dateien.
4. Führt die Einzelinformationen zu einer finalen JSON-Datei zusammen.
5. PDFs mit fehlgeschlagenen Extraktionen werden in einen Fehlerordner verschoben.
6. Für jede PDF wird im Ausgabeordner ein eigener Unterordner erstellt, 
   der alle zugehörigen extrahierten PDF-Dateien und JSON-Ergebnisse enthält.

Pfadangaben für Eingabe-, Ausgabe- und Fehlerordner sind am Ende des Skripts konfiguriert.
"""


import os
import json
import shutil
from split_pdfs_and_save import extract_between_words
from Extract_information_from_SDB.extract_information_part_03 import analyze_safety_data_sheet3
from Extract_information_from_SDB.extract_information_part_11 import analyze_safety_data_sheet11
from Extract_information_from_SDB.extract_information_part_12 import analyze_safety_data_sheet12
from Extract_information_from_SDB.process_and_merge_jsons import process_json_data

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
        success3 = extract_between_words(
            pdf_path,
            "Abschnitt3", "Erste-Hilfe-Maßnahmen",
            pdf_output_folder,
            ["Zusammensetzung", "ABSCHNITT3", "Angaben zu Bestandteilen", "3.2 Gemische", "SECTION 3", "ANGABEN ZU BESTANDTEILEN", "ABSCHNITT 3: Zusammensetzung/Angaben zu Bestandteilen"],
            ["ABSCHNITT4", "Erste-Hilfe-Maßnahmen", "SECTION 4", "ERSTE-HILFE-MASSNAHMEN", "ABSCHNITT 4: Erste-Hilfe Maßnahmen"],
            "_Abschnitt_3_extracted.pdf"
        )

        # Abschnitt 11
        success11 = extract_between_words(
            pdf_path,
            "ABSCHNITT 11: Toxikologische Angaben", "ABSCHNITT 12",
            pdf_output_folder,
            ["Abschnitt 11", "Toxikologische Angaben", "ANGABEN ZUR TOXIKOLOGIE", "Toxikologische Eigenschaften", "ABSCHNITT 11:", "11. ANGABEN ZUR TOXIKOLOGIE", "12. ANGABEN ZUR ÖKOLOGIE", "SECTION 11"],
            ["ABSCHNITT12", "Umweltbezogene Angaben", "ABSCHNITT 12:", "ANGABEN ZUR ÖKOLOGIE", "12.1", "SECTION 12"],
            "_Abschnitt_11_extracted.pdf"
        )

        # Abschnitt 12
        success12 = extract_between_words(
            pdf_path,
            "ABSCHNITT 12: Umweltbezogene Angaben", "Abschnitt 13",
            pdf_output_folder,
            ["Umweltbezogene Angaben", "12. ANGABEN ZUR ÖKOLOGIE", "ANGABEN ZUR ÖKOLOGIE", "Ökotoxische Wirkungen", "ABSCHNITT 12", "SECTION 12"],
            ["SECTION 13", "Entsorgung von Produkt", "Hinweise zur Entsorgung", "HINWEISE ZUR ENTSORGUNG", "13. HINWEISE ZUR ENTSORGUNG"],
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

        # JSON-Dateien kombinieren
        final_json = os.path.join(pdf_output_folder, f"{base_name}_final.json")
        try:
            process_json_data(jsonpath3, jsonpath11, jsonpath12, final_json)
            print(f"Verarbeitung abgeschlossen: {file_name}")
        except Exception as e:
            print(f"Fehler beim Kombinieren: {e}")
            create_empty_json(final_json)