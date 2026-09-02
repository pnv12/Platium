"""
Report Generator — створення звітів (TXT, JSON, HTML)
"""

import json
from datetime import datetime

def generate(data, output_path):
    """Генерує звіти у трьох форматах"""
    
    # TXT
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write(f"PLATIUM OSINT REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        for key, value in data.items():
            f.write(f"[{key.upper()}]\n")
            f.write(json.dumps(value, indent=2, ensure_ascii=False))
            f.write("\n\n")
    
    # JSON
    json_path = output_path.replace('.txt', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # HTML
    html_path = output_path.replace('.txt', '.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write("<html><head><title>Platium Report</title>")
        f.write("<style>body{font-family:monospace;background:#0a0a0a;color:#00ff00;padding:20px;}")
        f.write("table{border-collapse:collapse;width:100%;}th,td{border:1px solid #00ff00;padding:8px;text-align:left;}")
        f.write("</style></head><body>")
        f.write(f"<h1>Platium OSINT Report</h1><p>Generated: {datetime.now()}</p>")
        for key, value in data.items():
            f.write(f"<h2>{key.upper()}</h2><pre>{json.dumps(value, indent=2, ensure_ascii=False)}</pre>")
        f.write("</body></html>")
    
    return {"txt": output_path, "json": json_path, "html": html_path}
