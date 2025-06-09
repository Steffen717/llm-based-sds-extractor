import pandas as pd
import json
import re

# Diese Funktion liest eine Excel-Datei ein, verarbeitet die Daten und speichert sie als JSON-Datei
def excel_to_json(input_excel, output_json):
    def safe_str(val):
        """Wandelt den Wert in einen getrimmten String um und entfernt ein führendes Apostroph, falls vorhanden."""
        if pd.isna(val):
            return ""
        s = str(val).strip()
        if s.startswith("'"):
            s = s[1:]
        return s

    def extract_index_from_name(subst_str):
        """Extrahiere den Index aus dem Namen (wenn er in Klammern steht)."""
        match = re.search(r"\((\d+)\)", subst_str)
        return int(match.group(1)) if match else None

    def extract_index(subst_str):
        match = re.search(r"\((\d+)\)", subst_str)
        return int(match.group(1)) if match else None

    def split_sections(df, expected_tables=4):
        """
        Splittet df in genau expected_tables DataFrames.
        - Eine einzelne leere Zeile markiert das Ende eines Abschnitts.
        - Bei jeder zweiten aufeinanderfolgenden leeren Zeile wird eine fehlende Sub-Tabelle (leerer DF) eingefügt.
        """
        sections = []
        current_rows = []
        empty_count = 0

        for _, row in df.iterrows():
            if row.isnull().all():
                empty_count += 1
                if empty_count % 2 == 1:
                    # ungerade: Abschluss des aktuellen Abschnitts
                    if current_rows:
                        sections.append(pd.DataFrame(current_rows, columns=df.columns))
                        current_rows = []
                else:
                    # gerade: hier kommt eine fehlende Tabelle hin
                    sections.append(pd.DataFrame(columns=df.columns))
            else:
                # echte Datenzeile → zurücksetzen und aufnehmen
                empty_count = 0
                current_rows.append(row)

        # letzte Sammelzeilen als letzter Abschnitt
        if current_rows:
            sections.append(pd.DataFrame(current_rows, columns=df.columns))

        # Auffüllen, falls wir noch unter expected_tables sind
        while len(sections) < expected_tables:
            sections.append(pd.DataFrame(columns=df.columns))

        # Nur die ersten expected_tables zurückgeben
        return sections[:expected_tables]

    # Excel einlesen
    df_raw = pd.read_excel(input_excel, sheet_name="Daten", dtype=str)
    # In vier Abschnitte aufsplitten, fehlende Tabellen werden übersprungen
    sections = split_sections(df_raw, expected_tables=4)
    df_inhaltsstoffe, df_tox, df_ecotox, df_bcf = [s.reset_index(drop=True) for s in sections]

    # Abschnitt 1: gefährliche Inhaltsstoffe
    gefaehrlicheInhaltsstoffe = []
    name_to_index = {}
    for idx, row in df_inhaltsstoffe.iterrows():
        name = safe_str(row.get("Stoffname"))
        name_to_index[name] = idx

        nummern = safe_str(row.get("Nummern"))
        cas = re.search(r'CAS: ([^\n]*)', nummern)
        eg = re.search(r'EG: ([^\n]*)', nummern)
        indexnr = re.search(r'Index: ([^\n]*)', nummern)
        reach = re.search(r'REACH: ([^\n]*)', nummern)

        gefahr_raw = safe_str(row.get("Gefahrenkategorien und H-Sätze"))
        gefahr_liste, hsaetze_liste = [], []
        if gefahr_raw:
            for item in gefahr_raw.split(";\n"):
                if "-" in item:
                    h, g = item.split("-", 1)
                    hsaetze_liste.append(h.strip())
                    gefahr_liste.append(g.strip())
                elif item:
                    hsaetze_liste.append(item.strip())
                    gefahr_liste.append("")

        grenzen_raw = safe_str(row.get("Spezifische Konzentrationsgrenzen"))
        grenzen = []
        if grenzen_raw:
            for gr in grenzen_raw.split(";\n"):
                match = re.match(r"([^\-\n]+)-([^:]+): (.+)", gr)
                if match:
                    h, gk, sz = match.groups()
                    grenzen.append({
                        "hSaetze": h.strip(),
                        "gefahrenkategorie": gk.strip(),
                        "spezKonzGrenze": sz.strip()
                    })

        substanz = {
            "stoffname": name,
            "casNummer": cas.group(1).strip() if cas else "",
            "egNummer": eg.group(1).strip() if eg else "",
            "indexNummer": indexnr.group(1).strip() if indexnr else "",
            "reachNummer": reach.group(1).strip() if reach else "",
            "konzentration": safe_str(row.get("Konzentration")),
            "konzentrationEinheit": safe_str(row.get("Konzentrationseinheit")),
            "euhSaetze": safe_str(row.get("EUH-Sätze")).split(";\n") if safe_str(row.get("EUH-Sätze")) else [],
            "gefahrenkategorien": gefahr_liste,
            "hSaetze": hsaetze_liste,
            "mFaktorAkut": safe_str(row.get("M-Faktor Akut")),
            "mFaktorChronisch": safe_str(row.get("M-Faktor Chronisch")),
        }
        if grenzen:
            substanz["spezKonzGrenzen"] = grenzen

        gefaehrlicheInhaltsstoffe.append(substanz)

    # Abschnitt 2: Toxikologie
    tox = []
    for _, row in df_tox.iterrows():
        substanz_name = safe_str(row.get("Stoffname"))
        idx = extract_index_from_name(substanz_name)
        if idx is None:
            continue
        tox.append({
            "substanceIndex": idx,
            "typ": safe_str(row.get("Nummern")),
            "expositionsweg": safe_str(row.get("Konzentration")),
            "wert": safe_str(row.get("Konzentrationseinheit")),
            "einheit": safe_str(row.get("EUH-Sätze")),
            "methode": safe_str(row.get("Gefahrenkategorien und H-Sätze")),
            "spezies": safe_str(row.get("M-Faktor Akut")),
            "expositionsdauer": safe_str(row.get("M-Faktor Chronisch")),
        })

    # Abschnitt 3: EcoTox
    ecoTox = []
    for _, row in df_ecotox.iterrows():
        idx = extract_index(safe_str(row.get("Stoffname")))
        if idx is None:
            continue
        ecoTox.append({
            "substanceIndex": idx,
            "typ": safe_str(row.get("Nummern")),
            "spezies": safe_str(row.get("Konzentration")),
            "wert": safe_str(row.get("Konzentrationseinheit")),
            "einheit": safe_str(row.get("EUH-Sätze")),
            "methode": safe_str(row.get("Gefahrenkategorien und H-Sätze")),
            "trophieebene": safe_str(row.get("M-Faktor Akut")),
            "expositionsdauer": safe_str(row.get("M-Faktor Chronisch")),
        })

    # Abschnitt 4: BCF / LogKow
    if not df_bcf.empty:
        for _, row in df_bcf.iterrows():
            name = safe_str(row.get("Stoffname"))
            idx = name_to_index.get(name)
            if idx is not None:
                gefaehrlicheInhaltsstoffe[idx]["bcf"] = safe_str(row.get("BCF"))
                gefaehrlicheInhaltsstoffe[idx]["logKow"] = safe_str(row.get("LogKow"))
                gefaehrlicheInhaltsstoffe[idx]["biolAbbaubar"] = safe_str(row.get("Biologisch abbaubar"))

    # JSON Output
    json_output = {
        "gefaehrlicheInhaltsstoffe": gefaehrlicheInhaltsstoffe,
        "tox": tox,
        "ecoTox": ecoTox
    }

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(json_output, f, ensure_ascii=False, indent=2)