# LLM-based SDS Extractor

Ein **LLM-unterstütztes Extraktionswerkzeug**, das Sicherheitsdatenblätter (SDS) im PDF-Format verarbeitet, spezifische Abschnitte extrahiert und die Daten in strukturierte JSON-Dateien umwandelt. Es nutzt **OpenAI GPT** zur Analyse und Extraktion von Informationen aus den Abschnitten 3, 11 und 12 eines Sicherheitsdatenblatts.

## Funktionen

- **PDF-Extraktion**: Extrahiert die Abschnitte 3 (Angaben zu Bestandteilen), 11 (Toxikologische Angaben) und 12 (Umweltbezogene Angaben) aus SDS-PDF-Dateien.
- **LLM-Analyse**: Verwendet **OpenAI GPT**, um relevante Informationen aus den extrahierten Abschnitten zu analysieren und zu extrahieren.
- **Fehlerbehandlung**: PDFs, bei denen die Extraktion fehlschlägt, werden in einen Fehlerordner verschoben.
- **Kombinierte JSON-Ausgabe**: Die extrahierten und analysierten Daten werden in strukturierte JSON-Dateien umgewandelt und in einer finalen JSON-Datei zusammengeführt.
- **Batch-Verarbeitung**: Verarbeitet mehrere PDFs gleichzeitig aus einem Ordner und speichert die Ergebnisse in separaten Unterordnern.

## Voraussetzungen

- **Python 3.x** (empfohlen ab Version 3.6)
- **pip** (Python-Paketmanager)
- **OpenAI API Key** (für die Nutzung von GPT zur Analyse der Daten)

### Zusätzliche Abhängigkeiten

Installiere alle benötigten Python-Pakete:

```bash
pip install -r requirements.txt

