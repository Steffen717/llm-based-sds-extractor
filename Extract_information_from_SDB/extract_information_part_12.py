"""
Das Gleiche wier für Teil 3 mit Modell angepasst an Teil 12 des pdf 
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Umgebungsvariablen laden
load_dotenv()

# OpenAI-Client initialisieren
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class BCF_logkow(BaseModel):
    min: float
    minoperator: str
    max: float
    maxoperator: str

class Concentration(BaseModel):
    min: float
    minoperator: str
    max: float
    maxoperator: str
    unit: str

class ToxTests(BaseModel):
    expositionsdauer: float
    expositionsdauer_einheit: str
    trophieebene: str
    methode: str
    spezies: str
    typ: str = Field(None, description="LD50, ATE, EC50, EL50, Schätzwert der akuten Toxizität und Ähnliches")
    wert: Concentration

class Component(BaseModel):
    name: str           #BCF_logkow
    bcf: str            #BCF_logkow
    logPow: str
    ecotox: list[ToxTests]
    biologischabbaubar: str = Field( None,description="nein/nicht -> nicht abbaubar, leicht/ja -> schnell")
    casNo: str
    sonstiges: str

class DBAnalyst(BaseModel):
    components: list[Component]

def analyze_safety_data_sheet12(file_path: str, output_folder: str):
    file = client.files.create(
        file=open(file_path, "rb"),
        purpose="user_data"
    )
    print(f"Datei {file_path} hochgeladen")

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
                    "text": """Du bist ein Experte beim Analysieren von Sicherheitsdatenblättern. 
                                Extrahiere die Daten aus Abschnitt 12 und füge sie in das JSON-Schema ein. 
                                Ich will, dass du keine Veränderungen vornimmst. Falls ein Feld leer ist, setze einen leeren String und bei Zahlen (null) und füge alles richtig in das JSON-Schema ein. 
                                Füge bei Konzentration keine zusätzlichen Sachen ein, wenn nur ein Wert vorhanden ist, ist er nach dem Vorzeichen als Max oder Min einzuordnen. Mache keine Veränderungen, alles soll exakt so wie im PDF sein. 
                                Achte bei Trophäenebene und Spezies darauf, alle Informationen des PDFs richtig einzuordnen. 
                                Ich will Informationen zur biologischen Abbaubarkeit nur, wenn eine Aussage darüber gemacht wird, wie abbaubar es ist. 
                                Gib in Konzentration nur, wenn mehrere Werte im PDF vorkommen, mehrere Werte ein. 
                                LogPow auch immer alle Daten extrahieren und zuordnen. 
                                Trage ALLE Daten, die im PDF vorhanden sind, und lasse nichts aus. 
                                In Ecotox sollen alle Teile stehen, die Informationen, welche für Ecotox relevant sind und in das Schema passen, beinhalten. Wenn es für chronisch oder anderes ist, führe es trotzdem auf.
                                """,
                },
                ]
            }
        ],
        temperature=0.0,
        max_tokens=5000,
        response_format=DBAnalyst,
    )

    os.makedirs(output_folder, exist_ok=True)

    try:
        message_content = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError:
        print("Fehler beim Parsen der JSON-Antwort!")
        message_content = {}

    tokens_used = completion.usage.total_tokens if hasattr(completion, 'usage') else "Nicht verfügbar"

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

    output_file = os.path.join(
        output_folder,
        f"{os.path.splitext(os.path.basename(file_path))[0]}_result12.json"
    )
    with open(output_file, "w", encoding="utf-8") as result_file:
        json.dump(result_data, result_file, indent=4, ensure_ascii=False)

    print(f"Ergebnis gespeichert in {output_file}")
    print(f"Verwendete Tokens: {tokens_used}")
    return output_file