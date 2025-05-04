"""
Dieses Skript verarbeitet Informationen aus den Abschnitten 3, 11 und 12 eines Sicherheitsdatenblattes im JSON-Format. 
Es extrahiert, normalisiert und vereinheitlicht Angaben zu gefährlichen Inhaltsstoffen, toxikologischen und ökotoxikologischen Daten 
und fasst sie in einer strukturierten JSON-Datei zusammen.
"""

import json
import pandas as pd
import re
import unicodedata

def create_empty_json():
    return {
        "gefaehrlicheInhaltsstoffe": [],
        "ecoTox": [],
        "tox": []
    }

def normalize_operator(op):
    op = op.replace("≥", ">=").replace("≤", "<=").replace("-", "").strip()
    return "" if op == "=" else op

def clean_name(name: str) -> str:
    if not isinstance(name, str):
        return ""
    name = unicodedata.normalize("NFKC", name)
    name = name.lower()
    name = re.sub(r"\s+", "", name.strip()) 
    name = re.sub(r",\s*", ", ", name)
    name = re.sub(r"\s*([<>%])\s*", r"\1", name)
    return name

def update_json(data, update_data, key):
    if key in data and isinstance(data[key], list):
        data[key].extend(update_data)
    return data

def normalize_unit(unit, header_unit):
    return header_unit if unit.strip() == "%" else unit.strip()

def format_concentration(min_wert, min_operator, max_wert, max_operator, unit):
    if min_wert == 0:
        if min_operator not in [">", ">="]:
            min_operator = ""
    if max_wert == 0 and max_operator == "":
        return f"{min_operator}{min_wert}".strip()
    if max_wert == 0:
        return f"{min_operator}{min_wert}".strip()
    if max_operator == "" and max_wert != 0:
        max_operator = min_operator
    if min_wert is not None and max_wert is not None:
        if min_wert == max_wert:
            return f"{min_operator}{min_wert}".strip()
        return f"{min_operator}{min_wert} - {max_operator}{max_wert}".strip()
    if min_wert is not None:
        return f"{min_operator}{min_wert}".strip()
    if max_wert is not None:
        return f"{max_operator}{max_wert}".strip()
    return ""

def replace_zero(value, is_concentration=False):
    if value == 0 and not is_concentration:
        return ""
    return value

def parse_abschnitt_3(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        abschnitt_3 = json.load(f)
    substances = []
    substance_lookup = []
    tox_data = []
    header_unit = abschnitt_3["message"].get("Tabellen_header_Konzentrations_Einheit", "%")
    for comp in abschnitt_3["message"]["components"]:
        min_concentration = comp['concentration'].get('min')
        max_concentration = comp['concentration'].get('max')
        min_operator = normalize_operator(comp['concentration'].get('minoperator', ''))
        max_operator = normalize_operator(comp['concentration'].get('maxoperator', ''))
        unit_raw = comp['concentration'].get('unit', '')
        unit = normalize_unit(unit_raw, header_unit)
        concentration = format_concentration(min_concentration, min_operator, max_concentration, max_operator, unit)
        spez_konz_grenzen = []
        for scl in comp.get("specificConcentrationLimits", []):
            min_limit = scl['limit'].get('min')
            max_limit = scl['limit'].get('max')
            min_operator = normalize_operator(scl['limit'].get('minoperator', ''))
            max_operator = normalize_operator(scl['limit'].get('maxoperator', ''))
            unit_raw_spez = scl['limit'].get('unit', '')
            spez_konz_grenze = format_concentration(min_limit, min_operator, max_limit, max_operator, unit_raw_spez)
            if spez_konz_grenze:
                spez_konz_grenze += " " + unit_raw_spez
                spez_konz_grenzen.append({
                    "gefahrenkategorie": scl["category"],
                    "hSaetze": scl["hStatement"],
                    "spezKonzGrenze": spez_konz_grenze
                })
        substance = {
            "stoffname": comp["name"],
            "casNummer": replace_zero(comp.get("casNo")),
            "egNummer": replace_zero(comp.get("egNo")),
            "indexNummer": replace_zero(comp.get("indexNo")),
            "reachNummer": replace_zero(comp.get("reachRegNo")),
            "konzentration": concentration,
            "konzentrationEinheit": unit if unit else None,
            "gefahrenkategorien": [c["category"] for c in comp.get("classification", [])],
            "hSaetze": [c["hStatement"] for c in comp.get("classification", [])],
            "spezKonzGrenzen": spez_konz_grenzen if spez_konz_grenzen else None,
            "mFaktorAkut": replace_zero(comp.get("mFactorAcute")),
            "mFaktorChronisch": replace_zero(comp.get("mFactorChronic")),
            "euhSaetze": [e["Nummer"] for e in comp["EuhNr"]] if comp.get("EuhNr") else None,
            "bcf": replace_zero(comp.get("bcf")),
            "logKow": replace_zero(comp.get("logKow")),                                                
            # "bcf": format_concentration(
                            #   normalize_operator(comp.get("bcf", {}).get("minoperator", "")),
                            #   replace_zero(comp.get("bcf", {}).get("min")),
                            #   normalize_operator(comp.get("bcf", {}).get("maxoperator", "")),
                            #   replace_zero(comp.get("bcf", {}).get("max")),
                            # 
            # ), 
            # "logKow": format_concentration(
                            #   normalize_operator(comp.get("logKow", {}).get("minoperator", "")),
                            #   replace_zero(comp.get("logKow", {}).get("min")),
                            #   normalize_operator(comp.get("logKow", {}).get("maxoperator", "")),    
                            #   replace_zero(comp.get("logKow", {}).get("max")),            
            # ),
            "biolAbbaubar": replace_zero(comp.get("biolAbbaubar")),
        }
        substance = {k: v for k, v in substance.items() if v is not None}
        substances.append(substance)
        substance_lookup.append((comp["name"], comp.get("casNo")))
        for ate in comp.get("ATEWerte", []):
            min_wert = replace_zero(ate['wert'].get('min'))
            max_wert = replace_zero(ate['wert'].get('max'))
            min_operator = normalize_operator(ate['wert'].get('minoperator', ''))
            max_operator = normalize_operator(ate['wert'].get('maxoperator', ''))
            ate_unit_raw = ate['wert'].get('unit', '')
            ate_unit = normalize_unit(ate_unit_raw, header_unit)
            wert = format_concentration(min_wert, min_operator, max_wert, max_operator, ate_unit)
            tox_data.append({
                "substanceIndex": len(substances) - 1,
                "typ": "ATE",
                "expositionsweg": replace_zero(ate.get("expositionsweg", "")),
                "wert": wert.strip(),
                "einheit": ate_unit,
                "spezies": replace_zero(ate.get("spezies", "")),
                "methode": replace_zero(ate.get("methode", "")),
                "expositionsdauer": f"{replace_zero(ate.get('expositionsdauer', ''))} {replace_zero(ate.get('expositionsdauer_einheit', ''))}".strip()
            })
    return substances, substance_lookup, tox_data

def find_substance_index(substance_lookup, name, casNo):
    for index, (s_name, s_cas) in enumerate(substance_lookup):
        if name and clean_name(s_name) == clean_name(name):
            return index
        if not name and s_cas and casNo and str(s_cas).strip() == str(casNo).strip():
            return index
    return None

def parse_abschnitt_11(file_path, substance_lookup):
    with open(file_path, "r", encoding="utf-8") as f:
        abschnitt_11 = json.load(f)
    tox_data = []
    for comp in abschnitt_11["message"]["components"]:
        substance_index = find_substance_index(substance_lookup, comp["name"], comp["casNo"])
        for tox in comp["tox"]:
            min_wert = tox["wert"].get("min", 0)
            min_operator = normalize_operator(tox["wert"].get("minoperator", ""))
            max_operator = normalize_operator(tox["wert"].get("maxoperator", ""))
            max_wert = tox["wert"].get("max", 0)
            min_operator = "" if min_operator == "-" else min_operator
            max_operator = "" if max_operator == "-" else max_operator
            wert = format_concentration(min_wert, min_operator, max_wert, max_operator, tox["wert"].get("unit", ""))
            tox_data.append({
                "substanceIndex": substance_index,
                "typ": tox.get("typ", ""),
                "expositionsweg": tox.get("expositionsweg", ""),
                "wert": str(wert).replace(".", ","),
                "einheit": tox["wert"].get("unit", ""),
                "spezies": tox.get("spezies", ""),
                "methode": tox.get("methode", ""),
                "expositionsdauer": f"{tox.get('expositionsdauer', '')} {tox.get('expositionsdauer_einheit', '')}".strip()
            })
    return tox_data

def parse_abschnitt_12(file_path, substance_lookup, gefaehrliche_inhaltsstoffe):
    with open(file_path, "r", encoding="utf-8") as f:
        abschnitt_12 = json.load(f)
    eco_tox_data = []
    components = abschnitt_12.get("message", {}).get("components", [])
    for comp in components:
        name = comp.get("name", "")
        cas_no = comp.get("casNo", "")
        substance_index = find_substance_index(substance_lookup, name, cas_no)
        if substance_index is not None:
            gefaehrliche_inhaltsstoffe[substance_index]["bcf"] = replace_zero(comp.get("bcf"))
            gefaehrliche_inhaltsstoffe[substance_index]["biolAbbaubar"] = replace_zero(comp.get("biologischabbaubar"))
            gefaehrliche_inhaltsstoffe[substance_index]["logKow"] = replace_zero(comp.get("logPow"))
        for tox in comp.get("ecotox", []):
            wert_dict = tox.get("wert", {})
            min_wert = wert_dict.get("min", 0)
            min_operator = normalize_operator(wert_dict.get("minoperator", ""))
            max_wert = wert_dict.get("max", 0)
            max_operator = normalize_operator(wert_dict.get("maxoperator", ""))
            min_operator = "" if min_operator == "-" else min_operator
            max_operator = "" if max_operator == "-" else max_operator
            wert = format_concentration(min_wert, min_operator, max_wert, max_operator, wert_dict.get("unit", ""))
            eco_tox_data.append({
                "substanceIndex": substance_index,
                "typ": tox.get("typ", ""),
                "spezies": tox.get("spezies", ""),
                "methode": tox.get("methode", ""),
                "expositionsdauer": f"{tox.get('expositionsdauer', '')} {tox.get('expositionsdauer_einheit', '')}".strip(),
                "wert": str(wert).replace(".", ","),
                "einheit": wert_dict.get("unit", ""),
                "trophieebene": tox.get("trophieebene", "")
            })
    return eco_tox_data

file_abschnitt_3 = r"C:\Users\Steffen Kades\Desktop\ausgabe\004.175-Boettcherin_Gelb_Boettcher_20220104\004.175-Boettcherin_Gelb_Boettcher_20220104_Abschnitt_3_extracted_result3.json"
file_abschnitt_11 = r"C:\Users\Steffen Kades\Desktop\ausgabe\004.175-Boettcherin_Gelb_Boettcher_20220104\004.175-Boettcherin_Gelb_Boettcher_20220104_Abschnitt_11_extracted_result11.json"
file_abschnitt_12 = r"C:\Users\Steffen Kades\Desktop\ausgabe\004.175-Boettcherin_Gelb_Boettcher_20220104\004.175-Boettcherin_Gelb_Boettcher_20220104_Abschnitt_12_extracted_result12.json"
output_file = r"C:\Users\Steffen Kades\Desktop\ausgabe\004.175-Boettcherin_Gelb_Boettcher_20220104\jsonthingy.json"
def process_json_data(file_abschnitt_3, file_abschnitt_11, file_abschnitt_12, output_file):
    result = create_empty_json()
    substances, substance_lookup, tox_data_3 = parse_abschnitt_3(file_abschnitt_3)
    result["gefaehrlicheInhaltsstoffe"].extend(substances)
    result["tox"].extend(tox_data_3)
    tox_data_11 = parse_abschnitt_11(file_abschnitt_11, substance_lookup)
    result["tox"].extend(tox_data_11)
    eco_tox_data = parse_abschnitt_12(file_abschnitt_12, substance_lookup, result["gefaehrlicheInhaltsstoffe"])
    result["ecoTox"].extend(eco_tox_data)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

process_json_data(file_abschnitt_3, file_abschnitt_11, file_abschnitt_12, output_file)  