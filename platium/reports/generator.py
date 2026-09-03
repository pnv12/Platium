"""
Report Generator — створення звітів у форматах TXT, JSON, HTML
"""

import os
import json
from datetime import datetime
from platium.core.errors import ScannerError

# Визначаємо абсолютний шлях до папки звітів
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")

def _ensure_reports_dir():
    """Створює папку data/reports/, якщо її немає"""
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def generate(data, output_path=None):
    """
    Генерує звіти у трьох форматах: TXT, JSON, HTML.
    Якщо output_path не вказано, використовується шлях за замовчуванням.
    Повертає словник зі шляхами до згенерованих файлів.
    """
    if not data:
        raise ScannerError("No data to generate report")

    _ensure_reports_dir()

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"report_{timestamp}"
        output_path = os.path.join(REPORTS_DIR, base_name)

    # Створюємо базові шляхи
    base_path = output_path
    if not base_path.endswith(('.txt', '.json', '.html')):
        base_path = os.path.join(REPORTS_DIR, os.path.basename(output_path))

    txt_path = base_path + '.txt'
    json_path = base_path + '.json'
    html_path = base_path + '.html'

    # 1. TXT-звіт
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("PLATIUM OSINT REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        for key, value in data.items():
            f.write(f"[{key.upper()}]\n")
            f.write(json.dumps(value, indent=2, ensure_ascii=False))
            f.write("\n\n")

    # 2. JSON-звіт
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 3. HTML-звіт
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html><html><head><meta charset='utf-8'><title>Platium Report</title>")
        f.write("<style>body{font-family:monospace;background:#0a0a0a;color:#00ff00;padding:20px;}")
        f.write("h1{color:#00ff00;border-bottom:1px solid #00ff00;}")
        f.write("pre{background:#111;padding:10px;border:1px solid #333;overflow:auto;}")
        f.write("</style></head><body>")
        f.write(f"<h1>Platium OSINT Report</h1><p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        for key, value in data.items():
            # Екрануємо HTML-спецсимволи
            escaped_key = str(key).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            f.write(f"<h2>{escaped_key}</h2>")
            f.write(f"<pre>{json.dumps(value, indent=2, ensure_ascii=False)}</pre>")
        f.write("</body></html>")

    return {
        "txt": txt_path,
        "json": json_path,
        "html": html_path
    }
