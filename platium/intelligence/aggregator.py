import os
from datetime import datetime

from platium.core.result import ScanResult
from platium.core.normalizer import normalize_result, Normalizer
from platium.core.paths import DB_PATH
from platium.storage.database import (
    _get_connection,
    init_db,
    _get_or_create_entity,
    save_observation,
    save_relationship
)


def store_scan_result(result: ScanResult):
    """
    Зберігає результат сканування, використовуючи нормалізатор.
    """
    from platium.core.normalizer import Normalizer
    init_db()
    normalized = Normalizer.normalize(result)
    return normalized["entity_id"]


def find_connections(entity_value):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM entities WHERE value = ?", (entity_value,))
        row = cursor.fetchone()
        if not row:
            return []

        entity_id = row[0]

        cursor.execute('''
            SELECT e.value, r.relation_type, r.confidence, r.evidence
            FROM relationships r
            JOIN entities e ON r.target_entity_id = e.id
            WHERE r.source_entity_id = ?
        ''', (entity_id,))
        rows = cursor.fetchall()

        connections = []
        for row in rows:
            connections.append({
                "target": row[0],
                "relation": row[1],
                "confidence": row[2],
                "evidence": row[3]
            })
        return connections


def generate_analysis_report():
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM entities")
        entities_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM observations")
        observations_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM relationships")
        relationships_count = cursor.fetchone()[0]
        cursor.execute("SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type")
        type_stats = cursor.fetchall()

    return {
        "entities": entities_count,
        "observations": observations_count,
        "relationships": relationships_count,
        "type_distribution": dict(type_stats),
        "generated": datetime.now().isoformat()
    }
