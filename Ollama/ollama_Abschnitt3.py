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


image_folder = r"C:\Users\Steffen Kades\Desktop\bilderteil1"
image_paths = sorted(glob.glob(os.path.join(image_folder, "*.png")))

res = ollama.chat(
    model="gemma3:27b-it-qat",
    messages=[
        {
            "role": "user",
            "content":"""Du bist ein Experte beim Analysieren von Sicherheitsdatenblättern. Extrahiere die Daten aus Abschnitt 3 und füge sie in das JSON-Schema ein, der Inhalt ist im Kontext aufgeführt.
                        Jeder Stoff im Gemisch hat nur eine Konzentration. Achte darauf, immer alle Namen vollständig aufzuführen. 
                        Jeweils für den Maximalwert mit einem Vorzeichen und einen für den Minimalwert mit einem Vorzeichen.
                        Wenn in der Konzentration nur ein Maximalwert vorhanden ist, darf auch ausschließlich ein Max-Operator stehen, für Min genauso. 
                        Zusätzlich vermerke die genaue Prozent-Einheit, falls Informationen dazu vorhanden sind (Gewicht%, Vol%, oder nur % oder ähnliches).
                        Notiere in Tabellen_Header_Konzentrations_Einheit, falls irgendwo im PDF etwas in der Art steht. Exakt das, was im Dokument steht. 
                        Zusätzlich sollen Extrainformationen, die nicht in das restliche Schema passen, in „Sonstiges“ vermerkt werden. Vergiss keine Stoffe.
                        Falls es spezifische Konzentrationslimits gibt, packe sie an die jeweilige Stelle im JSON-Schema. 
                        Falls weder Max noch Min einen Wert haben, ist es keiner und wird nicht dort eingeordnet.
                        Falls etwas keinen Wert hat, soll es im Schema leer gelassen werden oder ein leerer String oder eine 0 sein. 
                        WICHTIG ich brauche in der classification liste immer die vollständigen Wertepaare H-nummer und die kategorie wie Acute Tox.4 mit der H nummer IMMER!!!
                        Im Folgenden Habe ich noch den Text der in den Bildern bin extrahiert Kontext: ABSCHNITT 3: Zusammensetzung/Angaben zu Bestandteilen
3.2.
Gemische
*
Beschreibung
Gefährliche Inhaltsstoffe
Einstufung gemäß Verordnung (EG) Nr. 1272/2008 [CLP]

EG-Nr.
CAS-Nr.
Index-Nr.
REACH-Nr.
Bezeichnung
Einstufung: // Bemerkung
Gew-%

612-290-00-1
Reaktionsprodukte
von
Paraformaldehyd
und
2-Hydroxypropylamim
(Verhältnis 3:2); [MBO]
Acute Tox. 4  H302  /  Acute Tox. 3 H311  /  Acute Tox. 4 H332  /  Skin Corr.
1B H314  /  Eye Dam. 1 H318  /  Skin Sens. 1A H317  /  Muta. 2 H341  /  Carc.
1B H350  /  STOT RE 2 H373  /  Aquatic Chronic 2 H411  /  EUH071
25 - 50

601-137-4
111905-53-4
Alcohols, C13-C15-branched and linear, butoxylated, ethoxylated
Acute Tox. 4  H302  /  Eye Irrit. 2 H319  /  Aquatic Chronic 3 H412
10 - 20

500-027-2
9043-30-5
Alcohol, iso-C13, ethoxylated (7-14 EO)
Acute Tox. 4  H302  /  Eye Dam. 1 H318
5 - 10

203-961-6
112-34-5
603-096-00-8
2-(2-butoxyethoxy)ethanol
Eye Irrit. 2  H319
5 - 10

203-473-3
107-21-1
603-027-00-1
Ethandiol
Acute Tox. 4  H302  /  STOT RE 2 H373
2,5 - 5

223-296-5
3811-73-2
Pyridin-2-thiol-1-oxid, Natriumsalz
Acute Tox. 4  H302  /  Acute Tox. 3 H311  /  Acute Tox. 4 H332  /  Skin Irrit. 2
H315  /  Eye Irrit. 2 H319  /  Aquatic Acute 1 H400 (M = 100)  /  Aquatic
Chronic 1 H410 (M = 10)
0,5 - 1
Sicherheitsdatenblatt
gemäß Verordnung (EG) Nr. 1907/2006 (REACH)
gemäß Verordnung (EU) 2020/878
Artikel-Nr.:
RSM008
Druckdatum:
02.11.2022
Version:
4.0
grotanol SR 2
Bearbeitungsdatum: 02.11.2022
DE
Ausgabedatum: 02.11.2022
Seite 3 / 11

200-001-8
50-00-0
605-001-00-5
Formaldehyd
Stoff mit einem gemeinschaftlichen Grenzwert (EG) für die Exposition am
Arbeitsplatz.
< 0,1

Zusätzliche Hinweise

Vollständiger Wortlaut der Einstufungen: siehe unter Abschnitt 16
Kennzeichnung der Inhaltsstoffe gemäß Verordnung EG Nr. 648/2004

5 - 15 %
nichtionische Tenside""",
            "images": image_paths,
        }
    ],
    format=DBAnalyst.model_json_schema(),
    options={"temperature": 0.0,
             "num_ctx": 30000}
)

print(res['message']['content'])