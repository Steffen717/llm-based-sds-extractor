import ollama
from pydantic import BaseModel, Field
import ollama
import json
import os
import glob

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
Kontext = """ABSCHNITT 12: Umweltbezogene Angaben

Einstufung gemäß Verordnung (EG) Nr. 1272/2008 [CLP]     
Nicht in die Kanalisation oder Gewässer gelangen lassen. 
12.1. Toxizität
*
Sehr giftig für Wasserorganismen.

Pyridin-2-thiol-1-oxid, Natriumsalz
Fischtoxizität, LC50, Oncorhynchus mykiss (Regenbogenforelle): 0,0066 mg/L   (96 h)
Daphnientoxizität, EC50, Daphnia magna: 0,022 mg/L   (48 h)
Algentoxizität, ErC50, Selenastrum capricornutum: 0,46 mg/L
Reaktionsprodukte von Paraformaldehyd und 2-Hydroxypropylamim (Verhältnis 3:2); [MBO]
Fischtoxizität, LC50, Danio rerio (Zebrabärbling): 71 mg/L   (96 h)
Daphnientoxizität, EC50, Daphnia pulex (Wasserfloh): 28 mg/L   (48 h)
Algentoxizität, ErC50, Pseudokirchneriella subcapitata: 2,95 mg/L   (72 h)
2-(2-butoxyethoxy)ethanol
Fischtoxizität, LC50: 1300 mg/L   (96 h)
Daphnientoxizität, EC50: 100 mg/L   (48 h)
Algentoxizität, ErC50    (96 h)

Langzeit Ökotoxizität
Giftig für Wasserorganismen, mit langfristiger Wirkung.  

12.2. Persistenz und Abbaubarkeit
*
Reaktionsprodukte von Paraformaldehyd und 2-Hydroxypropylamim (Verhältnis 3:2); [MBO]
: 89,8    (28 Tag(e)); Bewertung Leicht biologisch abbaubar (nach OECD-Kriterien)
Methode:  OECD 306
12.3. Bioakkumulationspotenzial
*
Reaktionsprodukte von Paraformaldehyd und 2-Hydroxypropylamim (Verhältnis 3:2); [MBO]
Verteilungskoeffizient n-Octanol/Wasser: -0,043
2-(2-butoxyethoxy)ethanol
Verteilungskoeffizient n-Octanol/Wasser:  1

Biokonzentrationsfaktor (BCF)
Toxikologische Daten liegen keine vor.
12.4. Mobilität im Boden
Toxikologische Daten liegen keine vor.
12.5. Ergebnisse der PBT- und vPvB-Beurteilung
Die Stoffe im Gemisch erfüllen nicht die PBT/vPvB Kriterien gemäß REACH, Anhang XIII.
12.6. Endokrinschädliche Eigenschaften

Es liegen keine Informationen vor.
12.7. Andere schädliche Wirkungen

Es liegen keine Informationen vor."""

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

print(res['message']['content'])