import os
import sqlite3
import json
from datetime import datetime
from platium.core.result import ScanResult
from platium.core.normalizer import normalize_result, Normalizer
from platium.core.paths import DB_PATH, ensure_dirs

def _get_connection():
    ensure_dirs()
    return sqlite3.connect(DB_PATH)

def init_db():
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                value TEXT NOT NULL UNIQUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                scanner TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                data TEXT,
                confidence REAL,
                evidence TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entity_id) REFERENCES entities (id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_entity_id INTEGER NOT NULL,
                target_entity_id INTEGER NOT NULL,
                relation_type TEXT NOT NULL,
                confidence REAL,
                evidence TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_entity_id) REFERENCES entities (id),
                FOREIGN KEY (target_entity_id) REFERENCES entities (id)
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_value ON entities (value)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_observations_entity_id ON observations (entity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships (source_entity_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships (target_entity_id)')
        conn.commit()

def _get_or_create_entity(entity_type, value):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM entities WHERE value = ?", (value,))
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            cursor.execute(
                "INSERT INTO entities (entity_type, value) VALUES (?, ?)",
                (entity_type, value)
            )
            conn.commit()
            return cursor.lastrowid

def save_observation(entity_id, scanner, source, status, data=None, confidence=0.0, evidence=None):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO observations (entity_id, scanner, source, status, data, confidence, evidence)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            entity_id,
            scanner,
            source,
            status,
            json.dumps(data) if data else None,
            confidence,
            evidence
        )
        )
        conn.commit()

def save_relationship(source_entity_id, target_entity_id, relation_type, confidence=0.0, evidence=None):
    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO relationships (source_entity_id, target_entity_id, relation_type, confidence, evidence)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            source_entity_id,
            target_entity_id,
            relation_type,
            confidence,
            evidence
        )
        )
        conn.commit()

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
