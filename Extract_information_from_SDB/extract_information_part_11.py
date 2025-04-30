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
    typ: str = Field(None, description="LD50, ATE, Schätzwert akuter Toxizität etc.")
    wert: Concentration = Field(
        None,
        description="Wenn nur ein Minimalwert vorhanden ist, gib nur diesen an – analog bei Maximalwert."
    )

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
                        "text": (
                            "Du bist ein Experte für die Analyse von Sicherheitsdatenblättern. "
                            "Extrahiere aus Abschnitt 11 des PDFs die toxikologischen Daten für inhalative, dermale und orale Werte "
                            "sowie ATE (Akute Toxizität) und überführe sie in das JSON-Schema – nur wenn diese Informationen vorhanden sind. "
                            "Gib toxikologische Angaben ausschließlich an, wenn sie im PDF vorhanden sind. "
                            "Wenn ein Wert fehlt, soll er als leerer String oder – bei Zahlen – als null dargestellt werden. "
                            "Das JSON-Schema soll immer vollständig ausgegeben werden. "
                            "Füge in der Konzentration nichts Zusätzliches ein. "
                            "Wenn nur ein Wert vorhanden ist, wird er je nach Vorzeichen als min oder max eingeordnet. "
                            "Das Feld 'tox' im Schema darf nur Einträge enthalten, wenn entsprechende Informationen im PDF stehen. "
                            "Mache keine Interpretationen oder inhaltlichen Änderungen – gib alles exakt so wieder, wie es im PDF steht. "
                            "Führe alle Stoffe auf, bei denen Informationen vorliegen – auch wenn Einträge mehrfach vorkommen. "
                            "Wenn ein Stoff z. B. mehrfach „oral“, „dermal“ oder „inhalativ“ vorkommt, sollen alle Versionen einzeln aufgenommen werden – "
                            "auch bei nur geringfügigen Unterschieden (z. B. anderer Wert oder andere Dauer). "
                            "Beim Eintrag 'expositionsweg' sollen Staub, Nebel, Gas, Dampf etc. immer exakt übernommen werden. "
                            "Verwende: 'inhalativ' bei 'einatmen', 'oral' bei 'schlucken'."
                        )
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
