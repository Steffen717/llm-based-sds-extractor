"""
Dieses Skript analysiert Sicherheitsdatenblätter (SDB), extrahiert Informationen aus Abschnitt 3
(Informationen zu Bestandteilen), und konvertiert diese in ein strukturiertes JSON-Format basierend 
auf einem definierten Pydantic-Datenschema. Dabei wird die Ollama-API verwendet, um den Inhalt automatisch
aus PDF-Dateien zu extrahieren und die relevanten Stoffdaten zu interpretieren. Die Ergebnisse werden 
in einer JSON-Datei im angegebenen Ausgabeordner gespeichert.
"""

import ollama
from pydantic import BaseModel, Field
import json
import os
import glob
from pydantic import BaseModel, Field
import json

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
    category: str = Field(..., description="Ausschließlich die Kategorie, ohne die H-Nummer")
    hStatement: str = Field(None, description="H-Nummer")

class Concentrationlimit(BaseModel):
    category: str = Field(None, description="Ausschließlich die Kategorie")
    hStatement: str = Field(None, description="H-Nummer")
    limit: Concentration

class ATE(BaseModel):
    expositionsdauer: float
    expositionsdauer_einheit: str
    expositionsweg: str = Field( ...,description="Wie wird es verabreicht: inhalativ (einatmen), inhalativ (Staub/Nebel),inhalativ (Gas), inhalativ (Dampf), dermal, oral (schlucken). Bei 'einatmen' verwende 'inhalativ', bei 'schlucken' verwende 'oral'.")
    methode: str
    spezies: str
    typ: str
    wert: Concentration

class Component(BaseModel):
    name: str
    casNo: str = Field(...)
    egNo: str = Field(...)
    indexNo: str = Field(...)
    reachRegNo: str = Field(...)
    EuhNr: list[EUHNummern] = Field(None, description="Nur Nummern mit EUH")
    concentration: Concentration
    specificConcentrationLimits: list[Concentrationlimit] = Field(None, description="Wenn bestimmte H-Nummern bestimmte Konzentrationen aufweisen")
    classification: list[Classification]
    mFactorAcute: float
    mFactorChronic: float
    ATEWerte: list[ATE] = Field(None, description="ATE WErte falls vorhanden")



class DBAnalyst(BaseModel):
    components: list[Component]
    Tabellen_header_Konzentrations_Einheit: str = Field(None, description="Gibt die genaue Konzentrationseinheit an, die im Tabellenkopf angegeben ist, wie vol%, gewicht% etc., oder im PDF angegeben ist, falls vorhanden.")


image_folder = ""
image_paths = sorted(glob.glob(os.path.join(image_folder, "*.png")))

Prompt = """Du bist ein Experte beim Analysieren von Sicherheitsdatenblättern. Extrahiere die Daten aus Abschnitt 3 und füge sie in das JSON-Schema ein, der Inhalt ist im Kontext aufgeführt.
                        Jeder Stoff im Gemisch hat nur eine Konzentration. Achte darauf, immer alle Namen vollständig aufzuführen. 
                        Jeweils für den Maximalwert mit einem Vorzeichen und einen für den Minimalwert mit einem Vorzeichen.
                        Wenn in der Konzentration nur ein Maximalwert vorhanden ist, darf auch ausschließlich ein Max-Operator stehen, für Min genauso. 
                        Zusätzlich vermerke die genaue Prozent-Einheit, falls Informationen dazu vorhanden sind (Gewicht%, Vol%, oder nur % oder ähnliches).
                        Notiere in Tabellen_Header_Konzentrations_Einheit, falls irgendwo im PDF etwas in der Art steht. Exakt das, was im Dokument steht. 
                        Vergiss keine Stoffe.
                        Falls es spezifische Konzentrationslimits gibt, packe sie an die jeweilige Stelle im JSON-Schema. 
                        Falls weder Max noch Min einen Wert haben, ist es keiner und wird nicht dort eingeordnet.
                        Falls etwas keinen Wert hat, soll es im Schema leer gelassen werden oder ein leerer String oder eine 0 sein. 
                        WICHTIG ich brauche in der classification liste immer die vollständigen Wertepaare H-nummer und die kategorie wie Acute Tox.4 mit der H nummer IMMER!!!"""
Kontext = """
"""

res = ollama.chat(
    model="gemma3:27b-it-qat",
    messages=[
        {
            "role": "user",
            "content":"""{Prompt} 
            Im Folgenden habe ich noch den Text der in den Bildern ist extrahiert nutze ihn um die Daten richtig zu extrahieren er kommt hier: {Kontext}""",
            "images": image_paths,
        }
    ],
    format=DBAnalyst.model_json_schema(),
    options={"temperature": 0.0,
             "num_ctx": 30000}
)

print(res['message']['content'])