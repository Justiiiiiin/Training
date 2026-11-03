"""Pfade fuer alle Tests: funktionieren aus jedem Ordner und auf jedem Rechner."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.environ.get("FC_APP_DIR", ROOT)
APP_FILE = os.path.join(APP_DIR, "index.html")
APP_URL = os.environ.get("FC_URL") or "file://" + APP_FILE
RECIPES_JSON = os.path.join(ROOT, "tools", "recipes", "recipes.json")
SHOTS = os.environ.get("FC_SHOTS") or os.path.join(os.environ.get("TMPDIR", "/tmp"), "fc-shots")
os.makedirs(SHOTS, exist_ok=True)
