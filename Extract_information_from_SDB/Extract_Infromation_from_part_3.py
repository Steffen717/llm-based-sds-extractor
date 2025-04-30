"""
Dieses Skript analysiert Sicherheitsdatenblätter (SDB), extrahiert Informationen aus Abschnitt 3
(Informationen zu Bestandteilen), und konvertiert diese in ein strukturiertes JSON-Format basierend 
auf einem definierten Pydantic-Datenschema. Dabei wird die OpenAI API verwendet, um den Inhalt automatisch
aus PDF-Dateien zu extrahieren und die relevanten Stoffdaten zu interpretieren. Die Ergebnisse werden 
in einer JSON-Datei im angegebenen Ausgabeordner gespeichert.
"""

import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv
import time
from pydantic import BaseModel, Field

# Laden der Umgebungsvariablen
load_dotenv()

# OpenAI-Client initialisieren
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class Value(BaseModel):
    min: float
    unit: float

class Concentration(BaseModel):
    min: float
    minoperator: str
    max: float
    maxoperator: str
    unit: str = Field(None, description="Die genaue Einheit im Kontext der Tabelle, falls es in einer Tabelle steht")

class EUHNummern(BaseModel):
    Nummer: str = Field(None, description="EUH-Nummern, wenn vorhanden")

class Classification(BaseModel):
    category: str = Field(None, description="Ausschließlich die Kategorie, ohne die H-Nummer")
    hStatement: str = Field(None, description="H-Nummer")

class Concentrationlimit(BaseModel):
    category: str = Field(None, description="Ausschließlich die Kategorie")
    hStatement: str = Field(None, description="H-Nummer")
    limit: Concentration

class ATE(BaseModel):
    expositionsdauer: float
    expositionsdauer_einheit: str
    expositionsweg: str = Field(
        None,
        description=(
            "Wie wird es verabreicht: inhalativ (einatmen), inhalativ (Staub/Nebel), "
            "inhalativ (Gas), inhalativ (Dampf), dermal, oral (schlucken). "
            "Bei 'einatmen' verwende 'inhalativ', bei 'schlucken' verwende 'oral'."
        )
    )
    methode: str
    spezies: str
    typ: str
    wert: Concentration

class Component(BaseModel):
    name: str
    casNo: str
    egNo: str
    indexNo: str
    reachRegNo: str
    EuhNr: list[EUHNummern]
    concentration: Concentration
    specificConcentrationLimits: list[Concentrationlimit] = Field(None, description="Wenn bestimmte H-Nummern bestimmte Konzentrationen aufweisen")
    classification: list[Classification]
    mFactorAcute: float
    mFactorChronic: float
    ATEWerte: list[ATE]
    sonstiges: str

class DBAnalyst(BaseModel):
    components: list[Component]
    Tabellen_header_Konzentrations_Einheit: str = Field(None, description="Gibt die genaue Konzentrationseinheit an, die im Tabellenkopf oder im PDF angegeben ist (z. B. Vol%, Gew%, %)")

def analyze_safety_data_sheet3(file_path, output_folder):
    # Output-Ordner erstellen
    os.makedirs(output_folder, exist_ok=True)
    
    # Datei hochladen
    file = client.files.create(
        file=open(file_path, "rb"),
        purpose="user_data"
    )
    print("Datei hochgeladen")

    # API-Anfrage
    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {"file_id": file.id}
                    },
                    {
                        "type": "text",
                        "text": """Du bist ein Experte beim Analysieren von Sicherheitsdatenblättern. Extrahiere die Daten aus Abschnitt 3 und füge sie in das JSON-Schema ein.
                        Jeder Stoff im Gemisch hat nur eine Konzentration. Achte darauf, immer alle Namen vollständig aufzuführen.
                        Jeweils für den Max-Wert mit einem Vorzeichen und einen für den Min-Wert mit einem Vorzeichen.
                        Wenn in der Konzentration nur ein Max-Wert vorhanden ist, darf ausschließlich ein Max-Operator stehen – für Min gilt dasselbe.
                        Zusätzlich vermerke die genaue Prozent-Einheit, falls Informationen dazu vorhanden sind: Gewichts-%, Volumen-%, nur %, o. Ä.
                        Notiere diese Information unter 'Tabellen_header_Konzentrations_Einheit', falls irgendwo im PDF ein entsprechender Hinweis steht.
                        Gib exakt das wieder, was im Dokument steht. Zusätzliche Informationen, die nicht in das restliche Schema passen, sollen unter 'sonstiges' vermerkt werden.
                        Vergiss keinen Stoff. Falls es spezifische Konzentrationslimits gibt, ordne sie der jeweiligen Stelle im JSON-Schema zu.
                        Wenn weder Max noch Min einen Wert haben, zählt es nicht als Grenze und soll nicht eingeordnet werden.
                        Wenn ein Wert fehlt, soll das Feld leer oder ein leerer String sein."""
                    },
                ]
            }
        ],
        temperature=0.0,
        max_tokens=5000,
        response_format=DBAnalyst,
    )

    # Token-Nutzung abrufen
    tokens_used = completion.usage.total_tokens if hasattr(completion, 'usage') else "Nicht verfügbar"

    # JSON-Daten verarbeiten
    try:
        message_content = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError:
        print("Fehler beim Parsen der JSON-Antwort!")
        message_content = {}

    # Ergebnis speichern
    result_data = {
        "pdf_name": os.path.basename(file_path),
        "message": message_content,
        "run_usage": {
            "completion_tokens": completion.usage.completion_tokens,
            "prompt_tokens": completion.usage.prompt_tokens,
            "total_tokens": tokens_used
        }
    }
    client.files.delete(file.id)

    output_file = os.path.join(output_folder, f"{os.path.splitext(os.path.basename(file_path))[0]}_result3.json")
    with open(output_file, "w", encoding="utf-8") as result_file:
        json.dump(result_data, result_file, indent=4, ensure_ascii=False)
    print(f"Ergebnis gespeichert in {output_file}")
    print(f"Verwendete Tokens: {tokens_used}")
    return output_file
