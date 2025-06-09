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
python Extract_information_from_SDB/main.py
```

### Funktionen der GUI:

- **Anzeige von Excel und PDF:** Auf der linken Seite wird das Excel-Dokument angezeigt, auf der rechten Seite das PDF.
  
- **Fehlerkorrektur und Zählung:** Fehler können direkt im Excel-Dokument auf der linken Seite korrigiert werden. Diese werden automatisch gezählt, sobald eine Zelle verändert wird. Die veränderten Zellen werden dabei markiert. Es besteht auch die Möglichkeit, manuell Fehler hinzuzufügen oder zu entfernen.

- **Navigation durch Ordner:** Du kannst zwischen verschiedenen PDFs navigieren, wenn mehrere extrahiert wurden, oder zum vorherigen Dokument zurückspringen. Beim Wechsel wird das Speichern der Änderungen automatisch ausgelöst.

- **Speichern der Änderungen:** Änderungen werden nicht automatisch gespeichert. Das Speichern erfolgt nur, wenn du zum nächsten PDF wechselst oder den entsprechenden Speichern-Button manuell drückst. Beim Speichern werden automatisch eine Excel-Datei mit den veränderten Daten erstellt und diese anschließend in eine korrigierte JSON-Datei umgewandelt.

- **Zeittracking:** Die Zeit wird während der Bearbeitung erfasst. Du kannst die Zeit stoppen, wenn du möchtest. Beim Wechsel zum nächsten Blatt wird der Timer automatisch wieder gestartet oder du kannst ihn manuell starten.

- **Auswertungs-Export:** Eine Auswertung des gesamten Datensatzes kann im Excel-Format exportiert werden, welche die Anzahl der Zellen, Zeilen, die benötigte Zeit, Fehler sowie den Namen des PDFs enthält.

- **Suche im PDF:** Du kannst das PDF nach bestimmten Wörtern durchsuchen und direkt zu den Stellen springen, die diese Wörter enthalten.

### Ausführen des Editors
```bash
python Editor_code/Editor.py
```
Dann öffnet sich ein Dialogfenster in dem der erstelle ordner vom vorherigen code ausgewählt werden muss


## Ollama

Als letztes gibt es noch den Ollama Ordner in dem man das gleiche noch mit Ollama testen kann aber dabei müssen die zwischenschritte manuell gemacht werden.

### Voraussetzungen

- Ollama von [https://ollama.com/](https://ollama.com/) installieren und das jeweilige Modell downloaden.  
- Bei Verwendung der API-Aufrufe muss Ollama aktiv sein.  
- Es muss ein vision-fähiges Modell benutzt werden, damit die Bildverarbeitung funktioniert.


### Ausführen von Ollama Teil
```bash
python Ollama/pdf_to_img.py
```
Damit werden die PDFs in Bilder umgewandelt und im angegebenen Ordner platziert.

```bash
python Ollama/text_extract.py
```
Gibt den Text aus, der sich im PDF befindet.

```bash
python Ollama/ollama_Abschnitt3.py > Abschnitt3.json
python Ollama/ollama_Abschnitt11.py > Abschnitt11.json
python Ollama/ollama_Abschnitt12.py > Abschnitt12.json
```
Die Skripte sind jeweils für die angegebenen Abschnitte gedacht. Hierbei müssen jeweils der Bilderordner und der Prompt aus textextract angegeben werden.

