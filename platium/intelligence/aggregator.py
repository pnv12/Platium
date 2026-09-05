"""
Aggregator — збереження результатів, Entity-Observation-Relationship модель
"""

import os
import sqlite3
import json
from datetime import datetime
from platium.core.result import ScanResult, ScanStatus

# Визначаємо шлях до бази даних
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "platium.db")

def _ensure_data_dir():
    """Створює папку data/, якщо її немає"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def init_db():
    """Ініціалізує базу даних з новою моделлю Entity-Observation-Relationship"""
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблиця сутностей (Entity)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT NOT NULL,      -- email, phone, username, ip, domain
            value TEXT NOT NULL UNIQUE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблиця спостережень (Observation)
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

    # Таблиця зв'язків (Relationship)
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

    # Індекси для швидкості
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_entities_value ON entities (value)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_observations_entity_id ON observations (entity_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships (source_entity_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships (target_entity_id)')

    conn.commit()
    conn.close()

def _get_or_create_entity(entity_type, value):
    """Отримує або створює сутність у базі"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM entities WHERE value = ?", (value,))
    row = cursor.fetchone()
    if row:
        entity_id = row[0]
    else:
        cursor.execute(
            "INSERT INTO entities (entity_type, value) VALUES (?, ?)",
            (entity_type, value)
        )
        entity_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return entity_id

def save_observation(entity_id, scanner, source, status, data=None, confidence=0.0, evidence=None):
    """Зберігає спостереження в базу"""
    conn = sqlite3.connect(DB_PATH)
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
    ))
    conn.commit()
    conn.close()

def save_relationship(source_entity_id, target_entity_id, relation_type, confidence=0.0, evidence=None):
    """Зберігає зв'язок між двома сутностями"""
    conn = sqlite3.connect(DB_PATH)
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
    ))
    conn.commit()
    conn.close()

def store_scan_result(result: ScanResult):
    """
    Зберігає результат сканування в базу.
    Створює сутності, спостереження та зв'язки на основі даних.
    """
    init_db()
    target = result.target
    scanner = result.scanner
    status = result.status.value
    data = result.data
    sources = result.sources

    # Визначаємо тип сутності на основі сканера
    entity_type = {
        "email": "email",
        "username": "username",
        "phone": "phone",
        "ip": "ip",
        "social": "username",
        "threat": "ip",
        "graph": "username",
        "darknet": "domain",
        "deep": "auto"
    }.get(scanner, "unknown")

    # Створюємо або отримуємо сутність
    entity_id = _get_or_create_entity(entity_type, target)

    # Зберігаємо спостереження
    for source, source_data in sources.items():
        status_str = source_data.get("status", "unknown")
        confidence = 0.5 if status_str in ("found", "success") else 0.1
        evidence = source_data.get("url") or source_data.get("message") or source_data.get("evidence")
        save_observation(
            entity_id=entity_id,
            scanner=scanner,
            source=source,
            status=status_str,
            data=source_data,
            confidence=confidence,
            evidence=evidence
        )

    # Додаємо зв'язки на основі даних
    if data:
        # Наприклад, якщо це email scanner і є breaches
        if scanner == "email" and "hibp" in data:
            breaches = data.get("hibp", [])
            if isinstance(breaches, list):
                for breach in breaches:
                    breach_entity_id = _get_or_create_entity("breach", breach)
                    save_relationship(
                        source_entity_id=entity_id,
                        target_entity_id=breach_entity_id,
                        relation_type="appears_in_breach",
                        confidence=0.9,
                        evidence=f"Found in {breach}"
                    )

        # Якщо це username scanner і є знайдені платформи
        if scanner == "username":
            for platform, info in data.items():
                if isinstance(info, dict) and info.get("status") == "found":
                    platform_entity_id = _get_or_create_entity("platform", platform)
                    save_relationship(
                        source_entity_id=entity_id,
                        target_entity_id=platform_entity_id,
                        relation_type="has_profile_on",
                        confidence=0.9,
                        evidence=info.get("url", "")
                    )

        # Якщо це phone scanner і є оператор
        if scanner == "phone":
            phone_data = data.get("data", {})
            if phone_data.get("operator"):
                operator = phone_data["operator"]
                operator_entity_id = _get_or_create_entity("operator", operator)
                save_relationship(
                    source_entity_id=entity_id,
                    target_entity_id=operator_entity_id,
                    relation_type="uses_operator",
                    confidence=0.9,
                    evidence=operator
                )

        # Якщо це ip scanner і є геолокація
        if scanner == "ip":
            location = data.get("location", {})
            if location.get("country"):
                country = location["country"]
                country_entity_id = _get_or_create_entity("country", country)
                save_relationship(
                    source_entity_id=entity_id,
                    target_entity_id=country_entity_id,
                    relation_type="located_in",
                    confidence=0.85,
                    evidence=country
                )

def find_connections(entity_value):
    """Знаходить зв'язки для заданої сутності"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM entities WHERE value = ?", (entity_value,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return []
    entity_id = row[0]

    cursor.execute('''
        SELECT e.value, r.relation_type, r.confidence, r.evidence
        FROM relationships r
        JOIN entities e ON r.target_entity_id = e.id
        WHERE r.source_entity_id = ?
    ''', (entity_id,))
    rows = cursor.fetchall()
    conn.close()

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
    """Генерує звіт на основі збережених даних"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM entities")
    entities_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM observations")
    observations_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM relationships")
    relationships_count = cursor.fetchone()[0]

    cursor.execute("SELECT entity_type, COUNT(*) FROM entities GROUP BY entity_type")
    type_stats = cursor.fetchall()

    conn.close()

    return {
        "entities": entities_count,
        "observations": observations_count,
        "relationships": relationships_count,
        "type_distribution": dict(type_stats),
        "generated": datetime.now().isoformat()
    }
