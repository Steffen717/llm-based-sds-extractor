import ollama
from pydantic import BaseModel, Field
import ollama
import json
import os
import glob
import sys
import ollama
from pydantic import BaseModel, Field
import json

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
    typ: str = Field(..., description="LD50, ATE, EC50, EL50, Schätzwert der akuten Toxizität und Ähnliches")
    wert: Concentration

class Component(BaseModel):
    name: str           
    bcf: str            #BCF_logkow
    logPow: str         #BCF_logkow
    ecotox: list[ToxTests]
    biologischabbaubar: str = Field( ...,description="nein/nicht -> nicht abbaubar, leicht/ja -> schnell")
    casNo: str

class DBAnalyst(BaseModel):
    components: list[Component]

image_folder = r"C:\Users\Steffen Kades\Desktop\Blatt 26\Teil12"
image_paths = sorted(glob.glob(os.path.join(image_folder, "*.png")))

Prompt = """Du bist ein Experte beim Analysieren von Sicherheitsdatenblättern. 
                                Extrahiere die Daten aus Abschnitt 12 welcher im Kontext angegeben ist und füge sie in das JSON-Schema ein. 
                                Ich will, dass du keine Veränderungen vornimmst. Falls ein Feld leer ist, setze einen leeren String und bei Zahlen (null) und füge alles richtig in das JSON-Schema ein. 
                                Füge bei Konzentration keine zusätzlichen Sachen ein, wenn nur ein Wert vorhanden ist, ist er nach dem Vorzeichen als Max oder Min einzuordnen. Mache keine Veränderungen, alles soll exakt so wie im PDF sein. 
                                Achte bei Trophäenebene und Spezies darauf, alle Informationen des PDFs richtig einzuordnen. 
                                Ich will Informationen zur biologischen Abbaubarkeit nur, wenn eine Aussage darüber gemacht wird, wie abbaubar es ist. 
                                Gib in Konzentration nur, wenn mehrere Werte im PDF vorkommen, mehrere Werte ein. 
                                LogPow auch immer alle Daten extrahieren und zuordnen. 
                                Bei Logkow und BCF sollen immer nur die Zahlen und deren Vorzeichen extrahiert werden, Zusatzinformationen wie pH-Wert, Temperatur und andere sollen ignoriert werden
                                Trage ALLE Daten, die im PDF vorhanden sind, und lasse nichts aus. 
                                In Ecotox sollen alle Teile stehen, die Informationen, welche für Ecotox relevant sind und in das Schema passen, beinhalten. Wenn es für chronisch oder anderes ist, führe es trotzdem auf. 
                                Wenn ein Feld nichts passt füge einen leeren String ein
                                Im Folgenden Habe ich noch den Text der in den Bildern bin extrahiert Kontext: ABSCHNITT 12: Umweltbezogene Angaben"""
Kontext = """"""

res = ollama.chat(
    model="gemma3:27b-it-qat",
    messages=[
        {
            "role": "user",
            "content":"""{Prompt} Im Folgenden habe ich noch den Text der in den Bildern ist extrahiert nutze ihn um die Daten richtig zu extrahieren er kommt hier: {Kontext}""",
            "images": image_paths,
        }
    ],
    format=DBAnalyst.model_json_schema(),
    options={"temperature": 0.0,
             "num_ctx": 30000}
)

with open(sys.argv[1], "w", encoding="utf-8") as result_file:
    json.dump({"message":json.loads(res['message']['content'])}, result_file, indent=4, ensure_ascii=False)