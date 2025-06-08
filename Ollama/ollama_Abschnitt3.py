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
    EuhNr: list[EUHNummern]
    concentration: Concentration
    specificConcentrationLimits: list[Concentrationlimit] = Field(None, description="Wenn bestimmte H-Nummern bestimmte Konzentrationen aufweisen")
    classification: list[Classification]
    mFactorAcute: float
    mFactorChronic: float
    ATEWerte: list[ATE] = Field(None, description="ATE WErte falls vorhanden")
    sonstiges: str

class DBAnalyst(BaseModel):
    components: list[Component]
    Tabellen_header_Konzentrations_Einheit: str = Field(None, description="Gibt die genaue Konzentrationseinheit an, die im Tabellenkopf angegeben ist, wie vol%, gewicht% etc., oder im PDF angegeben ist, falls vorhanden.")


image_folder = r"C:\Users\Steffen Kades\Desktop\Blatt11\Teil3"
image_paths = sorted(glob.glob(os.path.join(image_folder, "*.png")))

Prompt = """Du bist ein Experte beim Analysieren von Sicherheitsdatenblättern. Extrahiere die Daten aus Abschnitt 3 und füge sie in das JSON-Schema ein, der Inhalt ist im Kontext aufgeführt.
                        Jeder Stoff im Gemisch hat nur eine Konzentration. Achte darauf, immer alle Namen vollständig aufzuführen. 
                        Jeweils für den Maximalwert mit einem Vorzeichen und einen für den Minimalwert mit einem Vorzeichen.
                        Wenn in der Konzentration nur ein Maximalwert vorhanden ist, darf auch ausschließlich ein Max-Operator stehen, für Min genauso. 
                        Zusätzlich vermerke die genaue Prozent-Einheit, falls Informationen dazu vorhanden sind (Gewicht%, Vol%, oder nur % oder ähnliches).
                        Notiere in Tabellen_Header_Konzentrations_Einheit, falls irgendwo im PDF etwas in der Art steht. Exakt das, was im Dokument steht. 
                        Zusätzlich sollen Extrainformationen, die nicht in das restliche Schema passen, in „Sonstiges“ vermerkt werden. Vergiss keine Stoffe.
                        Falls es spezifische Konzentrationslimits gibt, packe sie an die jeweilige Stelle im JSON-Schema. 
                        Falls weder Max noch Min einen Wert haben, ist es keiner und wird nicht dort eingeordnet.
                        Falls etwas keinen Wert hat, soll es im Schema leer gelassen werden oder ein leerer String oder eine 0 sein. 
                        WICHTIG ich brauche in der classification liste immer die vollständigen Wertepaare H-nummer und die kategorie wie Acute Tox.4 mit der H nummer IMMER!!!"""
Kontext = """ ABSCHNITT 3: Zusammensetzung/Angaben zu Bestandteilen
3.2
Gemische
Gefährliche Inhaltsstoffe
AROMATISCHES POLYISOCYANAT ; CAS-Nr. : 53317-61-6
Gewichtsanteil:
2>60-<65%
Einstufung 1272/2008 [CLP] :
Skin Sens. 1 ; H317
Eye Irrit. 2 ; H319
XYLOL; REACH-Nr. : 01-2119488216-32 ; EG-Nr. : 215-535-7; CAS-Nr. : 1330-20-7
Gewichtsanteil :
Einstufung 1272/2008 [CLP] :
> 10-<15%
Flam. Liq. 3 ; H226 Asp. Tox. 1 ; H304 STOT RE 2 ; H373 Acute Tox. 4; H312
Acute Tox. 4; H332 Skin Irrit. 2 ; H315
Eye Irrit. 2 ; H319 STOT SE 3 ; H335
2-METHOXY-1-METHYLETHYLACETAT ; REACH-Nr. : 01-2119475791-29 ; EG-Nr. : 203-603-9; CAS-Nr. : 108-65-6
Seite: 2 / 11
(DE/ D)
Sicherheitsdatenblatt
gemäß Verordnung (EG) Nr. 1907/2006 (REACH)
•
Pe#ML
LACK- UND KUNSTSTOFF-CHEMIE GMBH
Artikel-Nr.:
Bearbeitungsdatum :
DX-1
15.01.2022
Druckdatum :
Version (Überarbeitung) :
26.01.2022
20.0.0 (19.0.0)
Gewichtsanteil:
2>10-<15%
Einstufung 1272/2008 [CLP]
:
Flam. Liq. 3;H226 STOT SE 3 ; H336
N-BUTYLACETAT ; REACH-Nr. : 01-2119485493-29 ; EG-Nr. : 204-658-1; CAS-Nr. : 123-86-4
Gewichtsanteil :
Einstufung 1272/2008 [CLP] :
> 10-<15%
Flam. Liq. 3;H226 STOT SE 3;H336
2,4-DIISOCYANAT-TOLUOL; REACH-Nr, : 01-2119486974-18 ; EG-Nr. : 209-544-5; CAS-Nr. : 584-84-9
Gewichtsanteil :
Einstufung 1272/2008 [CLP]
:
> 0,1-<0,5%
Acute Tox. 2;H330 Resp. Sens. 1;H334 Care. 2;H351 Skin Irrit. 2;H315 Skin
Sens. 1;H317
Eye Irrit. 2;H319 STOT SE 3 ; H335 Aquatic Chronic 3; H412
Zusätzliche Hinweise
Wortlaut der Gefahren- und EU Gefahrenhinweise: siehe ABSCHNITT 16.
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