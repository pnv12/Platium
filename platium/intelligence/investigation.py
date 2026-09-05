"""
Investigation Layer — управління розслідуваннями
"""

import sqlite3
import json
from datetime import datetime
from platium.intelligence.aggregator import DB_PATH

def init_investigation_db():
    """Створює таблиці для розслідувань"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Таблиця розслідувань
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Зв'язок між розслідуваннями та сутностями
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigation_entities (
            investigation_id INTEGER,
            entity_id INTEGER,
            added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (investigation_id, entity_id),
            FOREIGN KEY (investigation_id) REFERENCES investigations (id),
            FOREIGN KEY (entity_id) REFERENCES entities (id)
        )
    ''')

    # Нотатки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigation_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investigation_id INTEGER,
            content TEXT NOT NULL,
            author TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investigation_id) REFERENCES investigations (id)
        )
    ''')

    # Таймлайн
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigation_timeline (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            investigation_id INTEGER,
            entity_id INTEGER,
            event_type TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (investigation_id) REFERENCES investigations (id),
            FOREIGN KEY (entity_id) REFERENCES entities (id)
        )
    ''')

    conn.commit()
    conn.close()

def create_investigation(name, description=None, status='active'):
    """Створює нове розслідування"""
    init_investigation_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO investigations (name, description, status) VALUES (?, ?, ?)",
        (name, description, status)
    )
    investigation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return investigation_id

def get_investigation(investigation_id):
    """Отримує розслідування за ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, name, description, status, created_at, updated_at FROM investigations WHERE id = ?",
        (investigation_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "status": row[3],
            "created_at": row[4],
            "updated_at": row[5]
        }
    return None

def list_investigations():
    """Повертає список усіх розслідувань"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, status, created_at FROM investigations ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "description": r[2], "status": r[3], "created_at": r[4]} for r in rows]

def add_entity_to_investigation(investigation_id, entity_id):
    """Додає сутність до розслідування"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO investigation_entities (investigation_id, entity_id) VALUES (?, ?)",
        (investigation_id, entity_id)
    )
    conn.commit()
    conn.close()

def add_note_to_investigation(investigation_id, content, author=None):
    """Додає нотатку до розслідування"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO investigation_notes (investigation_id, content, author) VALUES (?, ?, ?)",
        (investigation_id, content, author)
    )
    conn.commit()
    conn.close()

def add_timeline_event(investigation_id, entity_id, event_type, description):
    """Додає подію до таймлайну розслідування"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO investigation_timeline (investigation_id, entity_id, event_type, description) VALUES (?, ?, ?, ?)",
        (investigation_id, entity_id, event_type, description)
    )
    conn.commit()
    conn.close()

def get_investigation_entities(investigation_id):
    """Отримує всі сутності, пов'язані з розслідуванням"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT e.id, e.entity_type, e.value
        FROM investigation_entities ie
        JOIN entities e ON ie.entity_id = e.id
        WHERE ie.investigation_id = ?
    ''', (investigation_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "type": r[1], "value": r[2]} for r in rows]

def get_investigation_notes(investigation_id):
    """Отримує всі нотатки розслідування"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, content, author, created_at FROM investigation_notes WHERE investigation_id = ? ORDER BY created_at DESC",
        (investigation_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "content": r[1], "author": r[2], "created_at": r[3]} for r in rows]

def get_investigation_timeline(investigation_id):
    """Отримує таймлайн розслідування"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT it.id, it.event_type, it.description, it.created_at, e.value
        FROM investigation_timeline it
        LEFT JOIN entities e ON it.entity_id = e.id
        WHERE it.investigation_id = ?
        ORDER BY it.created_at ASC
    ''', (investigation_id,))
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "type": r[1], "description": r[2], "timestamp": r[3], "entity": r[4]} for r in rows]
