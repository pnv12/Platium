"""
Report Generator — створення звітів
"""

import json
from datetime import datetime

def generate(data, output_path):
    """Генерує звіт у TXT та JSON"""
    
    # Текстовий звіт
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("="*50 + "\n")
        f.write(f"PLATIUM OSINT REPORT\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*50 + "\n\n")
        for key, value in data.items():
            f.write(f"[{key.upper()}]\n")
            f.write(json.dumps(value, indent=2, ensure_ascii=False))
            f.write("\n\n")
    
    # JSON-звіт
    json_path = output_path.replace('.txt', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
