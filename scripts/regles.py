"""
Règles de nettoyage appliquées par build_data.py.

ALIAS_STRUCTURES : nom saisi (normalisé : minuscules, sans accents ni ponctuation)
                   -> clé de la structure dans data/localisation_structures.csv.
                   Plusieurs saisies d'une même structure pointent vers la même clé
                   (doublons fusionnés).
NOMS_PROJETS     : "<_index de la réponse>.<rang du projet dans la réponse>" -> nom court
                   affiché sur la carte (le questionnaire ne demandait pas de nom de projet).
                   Deux lignes portant le même nom pour une même structure sont fusionnées.
PROJETS_IGNORES  : lignes de projet à écarter.
ACTIVITES_GENERALES : lignes qui décrivent l'activité courante d'une formation sanitaire
                   plutôt qu'une initiative numérique ; elles restent consultables mais
                   sont masquées par défaut.
"""

ALIAS_STRUCTURES = {
    "direction du systeme national d information sanitaire et de l informatique": "DSNISI",
    "integrate health": "IH",
    "infinitus clinicaa": "INFINITUS",
    "silina tech": "SILINA",
    "centre hospitalier universitaire de kara": "CHUK",
    "instance de protection des donnees a caractere personnel ipdcp togo": "IPDCP",
    "doctamob sarl u": "DOCTAMOB",
    "doctamob": "DOCTAMOB",
    "efha digitals sarl anciennement efha medicals sarlu": "EFHA",
    "dokitaeyes togo": "DOKITAEYES",
    "secretariat permanent du plan national de developpement sanitaire": "SPPNDS",
    "pharmaciz": "PHARMACIZ",
    "vcare": "VCARE",
    "centre de sante nukafu": "NUKAFU",
    "devego": "DEVEGO",
    "centre de sante de lome": "CSL",
    "cms gbetsogbe": "GBETSOGBE",
    "cms adetikope": "ADETIKOPE",
    "cms gbenyedji": "GBENYEDJI",
    "cms adawlato": "ADAWLATO",
    "togo health informatics association": "TOHIA",
    "cms katanga": "KATANGA",
    "cms kodjoviakope": "KODJOVIAKOPE",
    "cms be attikoume": "BEATTIKOUME",
    "intisante": "INTISANTE",
    "new innovation technological corporation": "NITCH",
    "medilink": "MEDILINK",
    "cms": "CMS",
    "groupe menadel international": "GMI",
}

NOMS_PROJETS = {
    "1.1": "Collecte des données sanitaires (SNIS)",
    "2.1": "Santé communautaire digitale (ASC et RFS)",
    "3.1": "SIH et application mobile patient",
    "3.2": "XrayVision - téléradiologie",
    "4.1": "SILINA MRS - système d'information hospitalier",
    "6.1": "Formation et outils de mise en conformité (données personnelles)",
    "7.1": "OpenClinic",
    "7.2": "Enregistrement électronique des naissances et décès",
    "7.3": "DHIS2",
    "7.4": "Santé Com",
    "7.5": "e.Ref Santé - référence électronique",
    "8.1": "Doctamob - SuperApp santé",
    "8.2": "Doctamob - SuperApp santé",
    "8.3": "Doctamob - SuperApp santé",
    "14.1": "Doctamob - SuperApp santé",
    "9.1": "Transfusafe et TransfusIO",
    "9.2": "Givers et Challenge MAD Togo",
    "9.3": "Klasseroom",
    "9.4": "evalab",
    "9.5": "AntibioTogo",
    "10.1": "DokitaEyes Mutualisée (ISPV-Africa)",
    "10.2": "DokitaEyes Mutualisée (ISPV-Africa)",
    "12.1": "Plateforme Pharmaciz",
    "15.1": "Soins curatifs, préventifs et promotion de la santé",
    "18.1": "Médecine, santé de la reproduction, surveillance et laboratoire",
    "19.1": "Soins curatifs, SMI/PF, vaccination, laboratoire, santé communautaire",
    "20.1": "Soins curatifs, SMI/PF, vaccination, laboratoire, santé communautaire",
    "23.1": "Extension nationale de la santé numérique",
    "23.2": "Application numérique nationale de santé",
    "24.1": "Disponibilité des données sanitaires",
    "24.2": "CEPIAC",
    "24.3": "CEPIAC",
    "24.4": "CEPIAC",
    "24.5": "CEPIAC",
    "25.1": "Programme de santé communautaire",
    "26.1": "Saisie des données dans DHIS2",
    "27.1": "IntiSanté - santé sexuelle et reproductive",
    "28.1": "Écosystème médical",
    "29.1": "MEDILINK - plateforme nationale intégrée de santé",
    "30.1": "Digitalisation du service de santé",
    "31.1": "Protection des données des patients",
}

PROJETS_IGNORES = set()

ACTIVITES_GENERALES = {"15.1", "18.1", "19.1", "20.1", "25.1"}
