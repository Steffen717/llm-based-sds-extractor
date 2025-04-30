import os
from process_pdf_folder import extract_sections_from_folder

def main():
    input_folder = r"Pfad\zu\deinem\eingabe_ordner"
    output_folder = r"Pfad\zu\deinem\ausgabe_ordner"
    failed_folder = r"Pfad\zu\deinem\fehler_ordner"
    
    extract_sections_from_folder(input_folder, output_folder, failed_folder)

if __name__ == "__main__":
    main()