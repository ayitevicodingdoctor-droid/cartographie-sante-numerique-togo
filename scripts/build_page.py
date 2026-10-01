"""
Assemble index.html (site GitHub Pages) à partir de scripts/template.html.

Usage : python scripts/build_page.py            -> index.html (charge data/data.js)
        python scripts/build_page.py --autonome -> carte_autonome.html (données intégrées,
                                                   un seul fichier à partager)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tpl = (ROOT / "scripts" / "template.html").read_text(encoding="utf-8")
vendor = ROOT / "scripts" / "vendor"
leaflet_css = (vendor / "leaflet.css").read_text(encoding="utf-8") + "\n" + (vendor / "MarkerCluster.css").read_text(encoding="utf-8")
tpl = tpl.replace("/*__LEAFLET_CSS__*/", leaflet_css)

LIBS = (
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.js"></script>\n'
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.js"></script>\n'
)
autonome = "--autonome" in sys.argv or "--artifact" in sys.argv
if autonome:
    data = (ROOT / "data" / "data.js").read_text(encoding="utf-8")
    scripts = LIBS + "<script>\n" + data + "\n</script>"
else:
    scripts = LIBS + '<script src="data/data.js"></script>'
tpl = tpl.replace("<!--__SCRIPTS__-->", scripts)

if "--artifact" in sys.argv:
    out = ROOT.parent / "artifact" / "cartographie.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(tpl, encoding="utf-8")
else:
    head, body = tpl.split("</style>", 1)
    page = ('<!doctype html>\n<html lang="fr">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "</style>\n</head>\n<body>\n" + body.strip() + "\n</body>\n</html>\n")
    out = ROOT / ("carte_autonome.html" if autonome else "index.html")
    out.write_text(page, encoding="utf-8")
print("écrit :", out)
