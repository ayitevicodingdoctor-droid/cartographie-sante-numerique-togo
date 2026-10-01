"""
Construit data/data.js à partir de l'export KoboToolbox (xlsx), du fichier de
localisation des structures et des limites administratives (geoBoundaries).

Usage : python scripts/build_data.py [chemin_export.xlsx]

Pour ajouter de nouvelles réponses : exporter de nouveau le formulaire depuis
KoboToolbox (format xlsx, "toutes les versions", libellés en français),
compléter si besoin data/localisation_structures.csv et scripts/regles.py, puis relancer.

Les données personnelles (noms, téléphones, e-mails des répondants et des
personnes de contact) et les scores d'évaluation des parties prenantes ne sont
pas exportés vers la carte publique.
"""
import csv
import json
import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

from regles import ALIAS_STRUCTURES, NOMS_PROJETS, PROJETS_IGNORES, ACTIVITES_GENERALES

ROOT = Path(__file__).resolve().parent.parent
XLSX = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "scripts" / "reponses_kobo.xlsx"
GEO = ROOT / "scripts" / "tgo_ADM2.geojson"
GEO0 = ROOT / "scripts" / "tgo_ADM0.geojson"
LOC = ROOT / "data" / "localisation_structures.csv"
OUT = ROOT / "data" / "data.js"

# ---------------------------------------------------------------- découpage
REGIONS = {
    "Grand Lomé": ["Golfe", "Agoè-Nyivé"],
    "Maritime": ["Lacs", "Vo", "Yoto", "Bas-Mono", "Zio", "Avé"],
    "Plateaux": ["Ogou", "Anié", "Est-Mono", "Moyen-Mono", "Haho", "Kloto", "Agou",
                 "Danyi", "Kpélé", "Amou", "Wawa", "Akébou"],
    "Centrale": ["Tchaoudjo", "Tchamba", "Sotouboua", "Blitta", "Mô"],
    "Kara": ["Kozah", "Binah", "Doufelgou", "Kéran", "Assoli", "Bassar", "Dankpen"],
    "Savanes": ["Tône", "Tandjoaré", "Kpendjal", "Kpendjal-Ouest", "Oti", "Oti-Sud", "Cinkassé"],
}
# Préfecture du questionnaire -> polygone geoBoundaries (découpage antérieur à 2019).
# Golfe et Agoè-Nyivé : le polygone « Lome Commune » sert pour Golfe, l'ancien
# polygone « Golfe » (périphérie nord) sert pour Agoè-Nyivé. Kpendjal-Ouest et
# Oti-Sud n'existent pas encore dans le fond : elles partagent le polygone parent.
PREF_TO_GEO = {
    "Golfe": "Lome Commune", "Agoè-Nyivé": "Golfe", "Avé": "Ave", "Kéran": "Keran",
    "Mô": "Plaine de Mô", "Tandjoaré": "Tandjouare", "Tône": "Tone",
    "Kpendjal-Ouest": "Kpendjal", "Oti-Sud": "Oti",
}
GEO_LABEL = {
    "Lome Commune": "Golfe (Lomé)", "Golfe": "Agoè-Nyivé", "Ave": "Avé", "Keran": "Kéran",
    "Plaine de Mô": "Mô", "Tandjouare": "Tandjoaré", "Tone": "Tône",
    "Kpendjal": "Kpendjal et Kpendjal-Ouest", "Oti": "Oti et Oti-Sud",
}


def geo_id(pref):
    return PREF_TO_GEO.get(pref, pref)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def flag(v):
    try:
        return float(v) == 1.0
    except (TypeError, ValueError):
        return False


def clean(v):
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return ""
    return re.sub(r"[ \t]+", " ", str(v)).strip()


def options(row, prefix, cols):
    """Liste des options cochées d'une question à choix multiples."""
    out = []
    for c in cols:
        if c.startswith(prefix + "/") and flag(row[c]):
            lab = c[len(prefix) + 1:]
            if lab.startswith("Autre"):
                continue
            out.append(lab)
    return out


# ---------------------------------------------------------------- lecture
xl = pd.ExcelFile(XLSX)
main = xl.parse(xl.sheet_names[0])
proj = xl.parse([s for s in xl.sheet_names if s.startswith("group_")][0])
mcols, pcols = list(main.columns), list(proj.columns)

loc = {r["cle"]: r for r in csv.DictReader(open(LOC, encoding="utf-8"))}

structures = {}
for _, r in main.iterrows():
    nom = clean(r["Nom officiel de l'organisation/structure/ entreprise / autres"])
    key = ALIAS_STRUCTURES.get(norm(nom))
    if key is None:
        print(f"[!] structure sans localisation : {nom!r} -> ajouter dans regles.ALIAS_STRUCTURES")
        continue
    autre_dom = clean(r.get("Préciser l'autre domaine numérique"))
    autre_out = clean(r.get("Préciser l'autre système utilisé"))
    s = structures.setdefault(key, {
        "id": key,
        "nom": loc[key]["nom_affiche"],
        "ville": loc[key]["ville"],
        "quartier": loc[key]["quartier"],
        "lat": float(loc[key]["latitude"]),
        "lng": float(loc[key]["longitude"]),
        "precision": loc[key]["precision"],
        "type": "",
        "nature": "",
        "zone": "",
        "financement": "",
        "implication": "",
        "domaines_numeriques": [],
        "outils": [],
        "coordination": "",
        "soumissions": [],
        "projets": [],
    })
    typ = clean(r["Type d'organisation"])
    prec = clean(r["Préciser le type d'organisation"])
    s["type"] = s["type"] or (prec if typ.startswith("Autre") and prec else typ)
    s["nature"] = "Porteur de projet / équipe" if "porteur de projet" in prec.lower() else "Personne morale"
    s["zone"] = s["zone"] or clean(r["Zone d'intervention"])
    s["financement"] = s["financement"] or clean(r["Source principale de financement"])
    imp = clean(r["Niveau d'implication avec la partie nationale"])
    imp = re.sub(r"\s*\(.*\)", "", imp).replace("natonales", "nationales").replace("  ", " ")
    s["implication"] = s["implication"] or imp
    s["coordination"] = s["coordination"] or clean(r["Participation aux réunions de coordination nationale en santé numérique"])
    for d in options(r, "Domaines numériques couverts", mcols) + ([autre_dom] if autre_dom else []):
        if d not in s["domaines_numeriques"]:
            s["domaines_numeriques"].append(d)
    for o in options(r, "Systèmes / outils numériques utilisés", mcols) + ([autre_out] if autre_out else []):
        if o not in s["outils"] and o != "Aucun / papier":
            s["outils"].append(o)
    s["soumissions"].append(int(r["_index"]))

idx_to_key = {}
for _, r in main.iterrows():
    nom = clean(r["Nom officiel de l'organisation/structure/ entreprise / autres"])
    if norm(nom) in ALIAS_STRUCTURES:
        idx_to_key[int(r["_index"])] = ALIAS_STRUCTURES[norm(nom)]

# ---------------------------------------------------------------- projets
projets = {}
rang = {}
for _, r in proj.iterrows():
    parent = int(r["_parent_index"])
    rang[parent] = rang.get(parent, 0) + 1
    ref = f"{parent}.{rang[parent]}"
    desc = clean(r["Description du programme / projet"])
    key = idx_to_key.get(parent)
    if key is None or ref in PROJETS_IGNORES or norm(desc) in ("", "ras", "nan", "pas de programmes"):
        continue
    nom = NOMS_PROJETS.get(ref) or (desc[:70] + ("…" if len(desc) > 70 else ""))
    pid = f"{key}::{norm(nom)}"

    regions_cochees = options(r, "Région(s) d'intervention (plusieurs choix possibles)", pcols)
    national = "Couverture nationale" in regions_cochees
    international = "International" in regions_cochees
    prefs = []
    for reg, liste in REGIONS.items():
        if reg not in regions_cochees:
            continue
        precisees = [p for p in liste if flag(r.get(f"Préfectures concernées – {reg}/{p}"))]
        prefs += precisees or liste  # région sans préfecture précisée = toute la région
    benef = options(r, "Bénéficiaires ciblés", pcols)
    autre_b = clean(r.get("Préciser les autres bénéficiaires"))
    if autre_b:
        benef.append(autre_b)

    p = projets.get(pid)
    if p is None:
        p = projets[pid] = {
            "id": pid, "structure": key, "nom": nom, "description": desc,
            "categorie": "activite" if ref in ACTIVITES_GENERALES else "numerique",
            "national": False, "international": False,
            "regions": [], "prefectures": [], "zones_geo": [], "beneficiaires": [],
        }
        structures[key]["projets"].append(pid)
    # fusion des doublons (même projet saisi plusieurs fois)
    if len(desc) > len(p["description"]):
        p["description"] = desc
    p["national"] |= national
    p["international"] |= international
    for reg in regions_cochees:
        if reg in REGIONS and reg not in p["regions"]:
            p["regions"].append(reg)
    for pr in prefs:
        if pr not in p["prefectures"]:
            p["prefectures"].append(pr)
        g = geo_id(pr)
        if g not in p["zones_geo"]:
            p["zones_geo"].append(g)
    for b in benef:
        if b not in p["beneficiaires"]:
            p["beneficiaires"].append(b)

for p in projets.values():
    if p["national"] and not p["zones_geo"]:
        p["portee"] = "nationale"
    elif p["zones_geo"]:
        p["portee"] = "ciblée" if not p["national"] else "nationale + zones précisées"
    elif p["international"]:
        p["portee"] = "internationale"
    else:
        p["portee"] = "non précisée"

# ---------------------------------------------------------------- géographie
geo = json.load(open(GEO, encoding="utf-8"))
pref_region = {geo_id(p): reg for reg, l in REGIONS.items() for p in l}


def rnd(c):
    if isinstance(c[0], (int, float)):
        return [round(c[0], 4), round(c[1], 4)]
    return [rnd(x) for x in c]


feats = []
for f in geo["features"]:
    g = f["properties"]["shapeName"]
    feats.append({
        "type": "Feature",
        "properties": {"id": g, "nom": GEO_LABEL.get(g, g), "region": pref_region.get(g, "")},
        "geometry": {"type": f["geometry"]["type"], "coordinates": rnd(f["geometry"]["coordinates"])},
    })
missing = set(pref_region) - {f["properties"]["id"] for f in feats}
assert not missing, missing

meta = {
    "titre": "Cartographie des acteurs de la santé numérique au Togo - 2026",
    "source": "Enquête « Cartographie des parties prenantes - Santé numérique Togo 2026 » (KoboToolbox)",
    "export": XLSX.name,
    "nb_reponses": int(len(main)),
    "nb_structures": len(structures),
    "nb_projets": len(projets),
    "nb_projets_numeriques": sum(p["categorie"] == "numerique" for p in projets.values()),
    "premiere_reponse": str(main["_submission_time"].min())[:10],
    "derniere_reponse": str(main["_submission_time"].max())[:10],
}

js = "/* Fichier généré par scripts/build_data.py - ne pas modifier à la main */\n"
js += "window.CARTO_META = " + json.dumps(meta, ensure_ascii=False) + ";\n"
js += "window.CARTO_STRUCTURES = " + json.dumps(list(structures.values()), ensure_ascii=False) + ";\n"
js += "window.CARTO_PROJETS = " + json.dumps(list(projets.values()), ensure_ascii=False) + ";\n"
pays = json.load(open(GEO0, encoding="utf-8"))["features"][0]["geometry"]
js += "window.CARTO_PAYS = " + json.dumps({"type": "Feature", "properties": {}, "geometry": {"type": pays["type"], "coordinates": rnd(pays["coordinates"])}}, separators=(",", ":")) + ";\n"
js += "window.CARTO_PREFECTURES = " + json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False, separators=(",", ":")) + ";\n"
OUT.write_text(js, encoding="utf-8")
print(json.dumps(meta, ensure_ascii=False, indent=1))
