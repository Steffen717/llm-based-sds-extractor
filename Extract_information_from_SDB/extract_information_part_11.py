"""
Das Gleiche wier für Teil 3 mit Modell angepasst an Teil 11 des pdf
"""

import os
import json
import time
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Laden der Umgebungsvariablen
load_dotenv()

# OpenAI-Client initialisieren
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

class Concentration(BaseModel):
    min: float
    minoperator: str
    max: float
    maxoperator: str
    unit: str

class ToxTests(BaseModel):
    expositionsdauer: float
    expositionsdauer_einheit: str
    expositionsweg: str = Field(None,description="Wie wird es verabreicht: inhalativ/(einatmen), inhalativ (Staub/Nebel), inhalativ (Gas), inhalativ (Dampf), dermal, oral/(verschlucken). Falls 'einatmen' im PDF steht, benutze inhalativ, und wenn 'schlucken' steht, benutze oral.")
    methode: str
    spezies: str
    typ: str = Field(None, description="LD50, ATE, Schätzwert der akuten Toxizität und Ähnliches")
    wert: Concentration = Field(None,description="Wenn nur ein Min-Wert existiert, führe auch nur diesen auf; für Max genauso.")

class Component(BaseModel):
    name: str
    tox: list[ToxTests]
    casNo: str
    sonstiges: str

class DBAnalyst(BaseModel):
    components: list[Component]

def analyze_safety_data_sheet11(file_path: str, output_folder: str):
    os.makedirs(output_folder, exist_ok=True)

    file = client.files.create(
        file=open(file_path, "rb"),
        purpose="user_data"
    )
    print("Datei hochgeladen")

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
                                    Extrahiere aus Abschnitt 11 des PDFs die toxikologischen Daten für die inhalativen,
                                    dermalen und oralen Werte sowie die ATE (Akute Toxizität) und füge sie in das JSON-Schema ein. 
                                    Falls vorhanden, ansonsten füge sie nicht ins JSON-Schema ein. 
                                    Achte darauf, alle Stoffe zu berücksichtigen und gib die toxikologischen Angaben nur an, falls diese vorhanden sind. 
                                    Wenn etwas nicht vorhanden ist, soll es als leerer String und, falls es sich um Zahlen handelt, mit (null) dargestellt werden. 
                                    Das JSON-Schema immer komplett ausgeben. 
                                    Füge bei Konzentration keine zusätzlichen Sachen ein, wenn nur ein Wert vorhanden ist, ist es nach dem Vorzeichen als Max oder Min einzuordnen. 
                                    Die Konzentration hat jeweils einen Max-Wert mit einem Vorzeichen und einen für den Min-Wert mit einem Vorzeichen. 
                                    Im Tox-Array vom Schema soll nur etwas aufgezählt werden, wenn Informationen für dieses im PDF stehen. 
                                    Mache keine Veränderungen, alles soll exakt so wie im PDF sein. 
                                    Führe ALLE Stoffe auf, bei denen es zutrifft, auch wenn einiges doppelt ist. Wenn ein Stoff in der gleichen Kategorie mehrmals etwas stehen hat und sich nur ein Wert ändert,
                                    kann es also mehrmals oral, dermal und inhalativ pro Stoff existieren. 
                                    Bei inhalativ soll auch Staub, Nebel, Gas, Dampf immer genau notiert werden im Expositionsweg."""
                    },
                ]
            }
        ],
        temperature=0.0,
        max_tokens=5000,
        response_format=DBAnalyst,
    )

    tokens_used = completion.usage.total_tokens if hasattr(completion, 'usage') else "Nicht verfügbar"

    try:
        message_content = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError:
        print("Fehler beim Parsen der JSON-Antwort!")
        message_content = {}

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
        f"{os.path.splitext(os.path.basename(file_path))[0]}_result11.json"
    )
    with open(output_file, "w", encoding="utf-8") as result_file:
        json.dump(result_data, result_file, indent=4, ensure_ascii=False)

    print(f"Ergebnis gespeichert in {output_file}")
    print(f"Verwendete Tokens: {tokens_used}")
    return output_file
