import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(DATA_DIR, "reports")
DB_PATH = os.path.join(DATA_DIR, "platium.db")
MODULES_DIR = os.path.join(BASE_DIR, "platium", "scanners")
CORES_DIR = os.path.join(BASE_DIR, "platium", "core")
UTILS_DIR = os.path.join(BASE_DIR, "platium", "utils")
CLI_DIR = os.path.join(BASE_DIR, "platium", "cli")

def ensure_dirs():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
