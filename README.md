# LLM-based SDS Extractor

Ein **LLM-unterstütztes Extraktionswerkzeug**, das Sicherheitsdatenblätter (SDS) im PDF-Format verarbeitet, spezifische Abschnitte extrahiert und die Daten in strukturierte JSON-Dateien umwandelt. Es nutzt **OpenAI API** zur Extraktion von Informationen aus den Abschnitten 3, 11 und 12 eines Sicherheitsdatenblatts.

## Funktionen

- **PDF-Extraktion**: Extrahiert die Abschnitte 3 (Angaben zu Bestandteilen), 11 (Toxikologische Angaben) und 12 (Umweltbezogene Angaben) aus SDS-PDF-Dateien.
- **LLM-Analyse**: Verwendet **OpenAI API**, um relevante Informationen aus den extrahierten Abschnitten zu extrahieren.
- **Fehlerbehandlung**: PDFs, bei denen die Extraktion fehlschlägt, werden in einen Fehlerordner verschoben.
- **Kombinierte JSON-Ausgabe**: Die extrahierten und analysierten Daten werden in strukturierte JSON-Dateien umgewandelt und in einer finalen JSON-Datei zusammengeführt.
- **Batch-Verarbeitung**: Verarbeitet mehrere PDFs gleichzeitig aus einem Ordner und speichert die Ergebnisse in separaten Unterordnern.
- **Individuelle Ordnerstruktur**: Für jedes PDF wird ein separater Ordner erstellt, in dem die extrahierten Abschnitte als separate JSON-Dateien sowie die finale zusammengeführte JSON-Datei gespeichert werden.

## Voraussetzungen

- **Python 3.x** (empfohlen ab Version 3.6)
- **pip** (Python-Paketmanager)
- **OpenAI API Key** (für die Nutzung von GPT zur Analyse der Daten)

### Zusätzliche Abhängigkeiten

Installiere alle benötigten Python-Pakete:

```bash
pip install -r requirements.txt
```
OpenAI API-Schlüssel einrichten
Um das LLM-based SDS Extractor mit OpenAI API zu nutzen, musst du einen OpenAI API-Schlüssel hinzufügen. Dieser Schlüssel wird benötigt, um die Daten aus den PDF-Dokumenten zu extrahieren.

Schritte:
Erstelle eine Datei mit dem Namen .env im Hauptverzeichnis des Projekts (dort, wo sich auch die README.md und andere Projektdateien befinden).
Öffne die .env-Datei und füge deinen OpenAI API-Schlüssel im folgenden Format hinzu:
```bash
OPENAI_API_KEY=dein_api_schluessel
```
Ersetze dein_api_schluessel mit deinem tatsächlichen OpenAI API-Schlüssel.

### Anleitung zum Nutzen des Scripts

1. Öffne die Datei `main.py` und passe die Pfade zu deinem Eingabe-, Ausgabe- und Fehlerordner an.  

    - **Eingabeordner**: Dieser Ordner sollte die PDF-Dateien enthalten, die du verarbeiten möchtest. Das Skript wird jede PDF in diesem Ordner durchgehen und die relevanten Abschnitte extrahieren.

    - **Ausgabeordner**: Für jede verarbeitete PDF wird ein Unterordner erstellt, der den gleichen Namen wie die PDF trägt. In diesem Unterordner werden die extrahierten Daten in verschiedenen Formaten gespeichert:
      - Extrahierte PDFs der einzelnen Abschnitte (z. B. Abschnitt 3, Abschnitt 11, Abschnitt 12).
      - Ein PDF mit den 3 Teilen kombiniert (dokument.pdf) welches dann im moment diesen namen benötigt für die Evaluationssoftware
      - JSON-Dateien mit den analysierten Daten für jeden Abschnitt (z. B. `result3.json`, `result11.json`, `result12.json`).
      - Eine finale JSON-Datei, die alle Ergebnisse zusammenführt.
      - Die finale JSON-Datei wird in eine Excel-Datei umgewandelt und als „Tabelle.xlsx“ gespeichert, welche momentan diesen Namen benötigt, um vom Evaluationstool korrekt verarbeitet zu werden.deln.

    - **Fehlerordner**: Wenn bei der Extraktion oder Analyse einer PDF ein Fehler auftritt, wird diese PDF in den Fehlerordner verschoben. Du kannst die fehlerhafte Datei später überprüfen. Das Skript setzt die Verarbeitung der anderen PDFs fort, auch wenn eine PDF fehlschlägt. Du kannst jedoch den Code so anpassen, dass das Skript sofort abbricht, wenn ein Fehler auftritt, anstatt fortzufahren und die fehlerhafte Datei nur zu verschieben.

2. Nach der Anpassung der Pfade kannst du das Skript ausführen:

```bash
python main.py
