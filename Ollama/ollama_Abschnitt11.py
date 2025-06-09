import ollama
from pydantic import BaseModel, Field
import ollama
import json
import os
import glob

import ollama
from pydantic import BaseModel, Field
import json

class Concentration(BaseModel):
    min: float
    minoperator: str
    max: float
    maxoperator: str
    unit: str

class ToxTests(BaseModel):
    expositionsdauer: float = Field(default=10, description="Zeitangabe als Zahl,wenn kein Wert vorhanden ist setzte 0 ein")
    expositionsdauer_einheit: str
    expositionsweg: str = Field(...,description="Wie wird es verabreicht: inhalativ/(einatmen), inhalativ (Staub/Nebel), inhalativ (Gas), inhalativ (Dampf), dermal, oral/(verschlucken). Falls 'einatmen' im PDF steht, benutze inhalativ, und wenn 'schlucken' steht, benutze oral.")
    methode: str
    spezies: str
    typ: str = Field(..., description="LD50, ATE, Schätzwert der akuten Toxizität und Ähnliches")
    wert: Concentration = Field(...,description="Wenn nur ein Min-Wert existiert, führe auch nur diesen auf; für Max genauso.")

class Component(BaseModel):
    name: str
    tox: list[ToxTests]
    casNo: str

class DBAnalyst(BaseModel):
    components: list[Component]

image_folder = r"C:\Users\Steffen Kades\Desktop\Blatt 26\Teil11"
image_paths = sorted(glob.glob(os.path.join(image_folder, "*.png")))

Prompt = """Du bist ein Experte beim Analysieren von Sicherheitsdatenblättern. 
                                    Extrahiere aus Abschnitt 11 des inhaltes im Kontext angegebenen toxikologischen Daten für die inhalativen,
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
                                    Bei inhalativ soll auch Staub, Nebel, Gas, Dampf immer genau notiert werden im Expositionsweg.
                                    Im Folgenden Habe ich noch den Text der in den Bildern bin extrahiert Kontext: ABSCHNITT 11: Toxikologische Angaben"""
Kontext = """"""

res = ollama.chat(
    model="gemma3:27b-it-qat",
    messages=[
        {
            "role": "user",
            "content":"""{Prompt}  Im Folgenden habe ich noch den Text der in den Bildern ist extrahiert nutze ihn um die Daten richtig zu extrahieren er kommt hier: {Kontext}""",
            "images": image_paths,
        }
    ],
    format=DBAnalyst.model_json_schema(),
    options={"temperature": 0.0,
             "num_ctx": 30000}
)

print(res['message']['content'])