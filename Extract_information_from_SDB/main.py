"""
Dieser code ruft die Funktion extract_sections_from_folder auf, um die Abschnitte aus den PDFs in einem Ordner zu extrahieren und in einem anderen Ordner zu speichern.
"""

import os
from process_pdf_folder import extract_sections_from_folder

def main():
    input_folder = ""
    output_folder = ""
    failed_folder = ""
    
    extract_sections_from_folder(input_folder, output_folder, failed_folder)

if __name__ == "__main__":
    main()