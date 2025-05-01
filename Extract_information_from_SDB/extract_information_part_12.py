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
    operator: str
    value: str

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
    typ: str = Field(None, description="LD50, ATE, EC50, EL50, Schätzwert akuter Toxizität etc.")
    wert: Concentration

class Component(BaseModel):
    name: float           #BCF_logkow
    bcf: float            #BCF_logkow
    logPow: str
    ecotox: list[ToxTests]
    biologischabbaubar: str = Field(
        None,
        description="nein/nicht -> nicht abbaubar, leicht/ja -> schnell"
    )
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
                        "text": (
                            "Du bist ein Experte für die Analyse von Sicherheitsdatenblättern. "
                            "Extrahiere aus Abschnitt 12 die ökotoxikologischen Daten und füge sie in das JSON-Schema ein. "
                            "Nimm keinerlei inhaltliche Veränderungen vor. Wenn ein Feld fehlt, verwende einen leeren String oder null bei Zahlen. "
                            "Bei Konzentrationen soll nur dann min und max ausgefüllt werden, wenn entsprechende Werte im PDF stehen – keine Ergänzungen. "
                            "Ordne Konzentrationswerte je nach Vorzeichen korrekt als min oder max ein. "
                            "Bei 'Trophieebene' und 'Spezies' sind alle im PDF vorhandenen Informationen exakt zu übernehmen. "
                            "Informationen zur biologischen Abbaubarkeit sollen nur enthalten sein, wenn explizit etwas über die Abbaubarkeit gesagt wird. "
                            "LogPow ist vollständig zu extrahieren. "
                            "Das Feld 'ecotox' soll alle Daten enthalten, die ökotoxikologisch relevant und strukturiert einordbar sind – "
                            "auch chronische Daten oder Werte außerhalb von Standardparametern. "
                            "Lass keine Angaben aus, die im PDF zu finden sind."
                        )
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