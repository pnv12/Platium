"""
Report Generator — створення звітів у форматах PDF, Markdown, HTML, JSON
"""

import os
import json
import sqlite3
from datetime import datetime
from platium.core.result import ScanResult, ScanStatus
from platium.intelligence.aggregator import DB_PATH

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REPORTS_DIR = os.path.join(BASE_DIR, "data", "reports")

def _ensure_reports_dir():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

def _get_entity_data(entity_value):
    """Отримує всі дані про сутність з бази"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, entity_type, value FROM entities WHERE value = ?", (entity_value,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    entity_id, entity_type, value = row

    # Отримуємо спостереження
    cursor.execute('''
        SELECT scanner, source, status, data, confidence, evidence, timestamp
        FROM observations
        WHERE entity_id = ?
        ORDER BY timestamp DESC
    ''', (entity_id,))
    observations = cursor.fetchall()

    # Отримуємо зв'язки (вихідні)
    cursor.execute('''
        SELECT e.value, r.relation_type, r.confidence, r.evidence
        FROM relationships r
        JOIN entities e ON r.target_entity_id = e.id
        WHERE r.source_entity_id = ?
    ''', (entity_id,))
    outgoing = cursor.fetchall()

    # Отримуємо зв'язки (вхідні)
    cursor.execute('''
        SELECT e.value, r.relation_type, r.confidence, r.evidence
        FROM relationships r
        JOIN entities e ON r.source_entity_id = e.id
        WHERE r.target_entity_id = ?
    ''', (entity_id,))
    incoming = cursor.fetchall()

    conn.close()

    return {
        "id": entity_id,
        "type": entity_type,
        "value": value,
        "observations": [
            {
                "scanner": obs[0],
                "source": obs[1],
                "status": obs[2],
                "data": json.loads(obs[3]) if obs[3] else None,
                "confidence": obs[4],
                "evidence": obs[5],
                "timestamp": obs[6]
            }
            for obs in observations
        ],
        "outgoing_relationships": [
            {
                "target": rel[0],
                "relation_type": rel[1],
                "confidence": rel[2],
                "evidence": rel[3]
            }
            for rel in outgoing
        ],
        "incoming_relationships": [
            {
                "source": rel[0],
                "relation_type": rel[1],
                "confidence": rel[2],
                "evidence": rel[3]
            }
            for rel in incoming
        ]
    }

def generate_report(target: str, output_format: str = "html") -> str:
    """
    Генерує звіт для заданої сутності у вказаному форматі.
    Формати: html, json, md, pdf (поки заглушка)
    """
    _ensure_reports_dir()
    data = _get_entity_data(target)
    if not data:
        raise ValueError(f"Entity '{target}' not found in database")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"report_{target}_{timestamp}"
    file_path = os.path.join(REPORTS_DIR, base_name)

    if output_format == "json":
        return _generate_json(data, file_path)
    elif output_format == "html":
        return _generate_html(data, file_path)
    elif output_format == "md":
        return _generate_markdown(data, file_path)
    elif output_format == "pdf":
        return _generate_pdf(data, file_path)  # поки заглушка
    else:
        raise ValueError(f"Unsupported format: {output_format}")

def _generate_json(data, file_path):
    """Генерує JSON-звіт"""
    json_path = file_path + ".json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return json_path

def _generate_html(data, file_path):
    """Генерує HTML-звіт"""
    html_path = file_path + ".html"
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write("<!DOCTYPE html><html><head><meta charset='utf-8'>")
        f.write("<title>Platium Report</title>")
        f.write("<style>body{font-family:monospace;background:#0a0a0a;color:#00ff00;padding:20px;}")
        f.write("h1,h2{color:#00ff00;border-bottom:1px solid #00ff00;}")
        f.write("pre{background:#111;padding:10px;border:1px solid #333;overflow:auto;}")
        f.write(".status-success{color:#00ff00;}")
        f.write(".status-error{color:#ff0000;}")
        f.write(".status-partial{color:#ffff00;}")
        f.write("table{border-collapse:collapse;width:100%;margin-top:10px;}")
        f.write("th,td{border:1px solid #333;padding:8px;text-align:left;}")
        f.write("</style></head><body>")
        f.write(f"<h1>Platium Investigation Report</h1>")
        f.write(f"<p><strong>Target:</strong> {data['value']}</p>")
        f.write(f"<p><strong>Entity Type:</strong> {data['type']}</p>")
        f.write(f"<p><strong>Generated:</strong> {datetime.now().isoformat()}</p>")

        # Observations
        f.write("<h2>Observations</h2>")
        if data['observations']:
            f.write("<table><tr><th>Scanner</th><th>Source</th><th>Status</th><th>Confidence</th><th>Evidence</th><th>Timestamp</th></tr>")
            for obs in data['observations']:
                status_class = "status-success" if obs['status'] == "success" else "status-error" if obs['status'] in ("error", "not_found") else "status-partial"
                f.write(f"<tr><td>{obs['scanner']}</td><td>{obs['source']}</td><td class='{status_class}'>{obs['status']}</td><td>{obs['confidence']}</td><td>{obs['evidence']}</td><td>{obs['timestamp']}</td></tr>")
            f.write("</table>")
        else:
            f.write("<p>No observations found.</p>")

        # Relationships
        f.write("<h2>Relationships</h2>")
        if data['outgoing_relationships'] or data['incoming_relationships']:
            f.write("<h3>Outgoing</h3>")
            if data['outgoing_relationships']:
                f.write("<table><tr><th>Target</th><th>Relation</th><th>Confidence</th><th>Evidence</th></tr>")
                for rel in data['outgoing_relationships']:
                    f.write(f"<tr><td>{rel['target']}</td><td>{rel['relation_type']}</td><td>{rel['confidence']}</td><td>{rel['evidence']}</td></tr>")
                f.write("</table>")
            else:
                f.write("<p>No outgoing relationships.</p>")

            f.write("<h3>Incoming</h3>")
            if data['incoming_relationships']:
                f.write("<table><tr><th>Source</th><th>Relation</th><th>Confidence</th><th>Evidence</th></tr>")
                for rel in data['incoming_relationships']:
                    f.write(f"<tr><td>{rel['source']}</td><td>{rel['relation_type']}</td><td>{rel['confidence']}</td><td>{rel['evidence']}</td></tr>")
                f.write("</table>")
            else:
                f.write("<p>No incoming relationships.</p>")
        else:
            f.write("<p>No relationships found.</p>")

        f.write("</body></html>")
    return html_path

def _generate_markdown(data, file_path):
    """Генерує Markdown-звіт"""
    md_path = file_path + ".md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Platium Investigation Report\n")
        f.write(f"**Target:** {data['value']}\n")
        f.write(f"**Entity Type:** {data['type']}\n")
        f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")

        f.write("## Observations\n")
        if data['observations']:
            f.write("| Scanner | Source | Status | Confidence | Evidence | Timestamp |\n")
            f.write("|---------|--------|--------|------------|----------|-----------|\n")
            for obs in data['observations']:
                f.write(f"| {obs['scanner']} | {obs['source']} | {obs['status']} | {obs['confidence']} | {obs['evidence']} | {obs['timestamp']} |\n")
        else:
            f.write("No observations found.\n")

        f.write("\n## Relationships\n")
        f.write("### Outgoing\n")
        if data['outgoing_relationships']:
            f.write("| Target | Relation | Confidence | Evidence |\n")
            f.write("|--------|----------|------------|----------|\n")
            for rel in data['outgoing_relationships']:
                f.write(f"| {rel['target']} | {rel['relation_type']} | {rel['confidence']} | {rel['evidence']} |\n")
        else:
            f.write("No outgoing relationships.\n")

        f.write("\n### Incoming\n")
        if data['incoming_relationships']:
            f.write("| Source | Relation | Confidence | Evidence |\n")
            f.write("|--------|----------|------------|----------|\n")
            for rel in data['incoming_relationships']:
                f.write(f"| {rel['source']} | {rel['relation_type']} | {rel['confidence']} | {rel['evidence']} |\n")
        else:
            f.write("No incoming relationships.\n")
    return md_path

def _generate_pdf(data, file_path):
    """Генерує PDF-звіт (заглушка)"""
    # Для реального PDF потрібна бібліотека reportlab або weasyprint
    # Поки просто повертаємо помилку
    raise NotImplementedError("PDF generation is not yet implemented.")
