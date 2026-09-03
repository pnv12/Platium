"""
Report Generator — створення звітів у TXT, JSON, HTML
"""

import json
from datetime import datetime

def generate_report(data, output_path, format="txt"):
    """
    Генерує звіт у вказаному форматі
    data: словник з результатами
    output_path: шлях до файлу (без розширення)
    format: txt, json, html
    """
    if format == "txt":
        return _generate_txt(data, output_path)
    elif format == "json":
        return _generate_json(data, output_path)
    elif format == "html":
        return _generate_html(data, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}")

def _generate_txt(data, output_path):
    """Генерує текстовий звіт"""
    path = f"{output_path}.txt"
    with open(path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write(f"PLATIUM REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        for key, value in data.items():
            f.write(f"[{key.upper()}]\n")
            f.write(json.dumps(value, indent=2, ensure_ascii=False))
            f.write("\n\n")
    return path

def _generate_json(data, output_path):
    """Генерує JSON-звіт"""
    path = f"{output_path}.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return path

def _generate_html(data, output_path):
    """Генерує HTML-звіт"""
    path = f"{output_path}.html"
    with open(path, 'w', encoding='utf-8') as f:
        f.write("<html><head><title>Platium Report</title>")
        f.write("<style>body{font-family:monospace;background:#0a0a0a;color:#00ff00;padding:20px;}")
        f.write("h1{color:#00ff00;}pre{background:#1a1a1a;padding:10px;border-left:3px solid #00ff00;}")
        f.write("</style></head><body>")
        f.write(f"<h1>Platium OSINT Report</h1>")
        f.write(f"<p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>")
        for key, value in data.items():
            f.write(f"<h2>{key.upper()}</h2>")
            f.write(f"<pre>{json.dumps(value, indent=2, ensure_ascii=False)}</pre>")
        f.write("</body></html>")
    return path
