# Cartographie des acteurs de la santé numérique au Togo - 2026

Carte interactive des structures (personnes morales et porteurs de projet) ayant répondu à l'enquête « Cartographie des parties prenantes - Santé numérique Togo 2026 », et des initiatives de santé numérique qu'elles déploient.

- **points verts** : structures porteuses, positionnées à leur siège ; le chiffre indique le nombre d'initiatives déclarées ;
- **zones jaunes** : préfectures couvertes par les initiatives de la structure ou de l'initiative sélectionnée, avec le nom de chaque initiative ;
- **fond gradué** : nombre d'initiatives ciblant explicitement chaque préfecture ;
- un clic sur une préfecture liste les initiatives qui la couvrent et les structures qui y sont implantées.

## Contenu du dépôt

```
index.html                        page publiée (GitHub Pages)
carte_autonome.html               même carte en un seul fichier (données intégrées), à partager par e-mail
data/data.js                      données générées (structures, initiatives, préfectures)
data/localisation_structures.csv  coordonnées des structures - à corriger ici
scripts/build_data.py             export Kobo (xlsx) -> data/data.js
scripts/regles.py                 fusion des doublons, noms courts des initiatives
scripts/build_page.py             template.html -> index.html / carte_autonome.html
scripts/template.html             code de la page (HTML, CSS, JavaScript)
scripts/tgo_ADM0/ADM2.geojson     limites du pays et des préfectures (geoBoundaries)
```

## Publier sur GitHub Pages

1. créer un dépôt public (par exemple `cartographie-sante-numerique-togo`) et y déposer le contenu de ce dossier ;
2. dans le dépôt : **Settings > Pages > Build and deployment**, source « Deploy from a branch », branche `main`, dossier `/ (root)` ;
3. la carte est accessible après une à deux minutes à l'adresse `https://<votre-compte>.github.io/cartographie-sante-numerique-togo/`.

Aucune clé d'API ni serveur n'est nécessaire : la carte utilise Leaflet (bibliothèque libre) et le fond « Canvas » gris d'Esri, utilisable sans clé. Les serveurs d'OpenStreetMap ont été écartés car ils bloquent les pages ouvertes en local ou intégrées (« Access blocked ») ; CARTO exige désormais une clé.

## Mettre à jour les données

```bash
pip install pandas openpyxl
# 1. remplacer scripts/reponses_kobo.xlsx par le nouvel export KoboToolbox (xlsx, libellés français)
# 2. ajouter les nouvelles structures dans data/localisation_structures.csv et scripts/regles.py
python scripts/build_data.py
python scripts/build_page.py
python scripts/build_page.py --autonome
```

Le script signale toute structure qui n'a pas encore de localisation.

## Choix de représentation

- **Leaflet plutôt que Google Maps** : Google Maps exige une clé d'API liée à un compte de facturation, exposée dans le code public ; Leaflet avec un fond Esri est gratuit, sans clé, et s'héberge directement sur GitHub Pages ;
- **points pour les porteurs, polygones pour les initiatives** : une structure a un siège (un point), alors qu'une initiative couvre un territoire (des préfectures) ; deux couleurs distinctes séparent les deux niveaux ;
- **regroupement des points** : 26 des 28 structures sont dans le Grand Lomé ; les points proches sont regroupés et se séparent au zoom ;
- **couverture nationale à part** : 16 initiatives se déclarent nationales ; les colorier toutes sur l'ensemble du pays masquerait les initiatives ciblées, elles sont donc signalées par un contour pointillé et comptées séparément.

## Limites

- le questionnaire ne recueillait pas d'adresse : les positions sont approximatives (quartier connu ou siège présumé) et doivent être confirmées dans `data/localisation_structures.csv` ; ajouter une question GPS au formulaire Kobo réglerait ce point pour les prochaines collectes ;
- le questionnaire ne demandait pas de nom d'initiative : un nom court a été attribué à partir de la description (`scripts/regles.py`) ;
- les limites geoBoundaries datent d'avant le redécoupage de 2019 : Golfe et Agoè-Nyivé sont représentées par l'ancienne commune de Lomé et l'ancienne préfecture du Golfe ; Kpendjal-Ouest et Oti-Sud par leur préfecture d'origine.

## Données personnelles

La carte ne publie ni les noms, fonctions et coordonnées des répondants et personnes de contact, ni les scores d'influence, d'intérêt et de confiance, ni les analyses forces / faiblesses. Le fichier `scripts/reponses_kobo.xlsx` contient ces informations : **ne pas le déposer sur un dépôt public** (il est exclu par `.gitignore`).

## Sources et licences

- données : enquête « Cartographie des parties prenantes - Santé numérique Togo 2026 » (KoboToolbox) ;
- limites administratives : [geoBoundaries](https://www.geoboundaries.org), Runfola et al. (2020), CC BY 4.0 ;
- fond de plan : Esri World Light/Dark Gray Canvas (© Esri, HERE, Garmin, contributeurs OpenStreetMap) ;
- bibliothèques : Leaflet 1.9.4 (BSD-2), Leaflet.markercluster 1.5.3 (MIT).
