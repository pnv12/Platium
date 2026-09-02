#!/usr/bin/env python3
"""
Data Aggregator — зберігання, аналіз та виявлення зв'язків
Автор: Neo
Версія: 1.0
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from modules.utils import print_status

DB_PATH = "data/platium.db"

def init_db():
    """Ініціалізація бази даних"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS targets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            type TEXT NOT NULL,
            data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            relation TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pattern TEXT NOT NULL,
            count INTEGER DEFAULT 0,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_search(query, query_type, data):
    """Зберігає результати пошуку в базу"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO targets (query, type, data, timestamp) VALUES (?, ?, ?, ?)",
        (query, query_type, json.dumps(data), datetime.now())
    )
    conn.commit()
    conn.close()
    print_status(f"✅ Дані збережено для {query}", "success")

def find_connections(query):
    """Знаходить зв'язки між цілями"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT query, data FROM targets WHERE data LIKE ?",
        (f'%{query}%',)
    )
    rows = cursor.fetchall()
    conn.close()
    connections = []
    for row in rows:
        try:
            data = json.loads(row[1])
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and 'error' not in value:
                        connections.append({
                            "source": row[0],
                            "target": query,
                            "relation": key
                        })
        except:
            pass
    return connections

def extract_patterns():
    """Аналізує закономірності з бази"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Останні 100 запитів
    cursor.execute(
        "SELECT query, type, timestamp FROM targets ORDER BY timestamp DESC LIMIT 100"
    )
    rows = cursor.fetchall()
    conn.close()
    patterns = {}
    for row in rows:
        query, type_, ts = row
        # Аналіз за типом
        key = f"{type_}:{query[:10]}"
        patterns[key] = patterns.get(key, 0) + 1
    return patterns

def generate_analysis_report():
    """Генерує звіт на основі збережених даних"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Загальна статистика
    cursor.execute("SELECT COUNT(*) FROM targets")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM connections")
    connections_count = cursor.fetchone()[0]
    cursor.execute("SELECT type, COUNT(*) FROM targets GROUP BY type")
    type_stats = cursor.fetchall()
    conn.close()
    report = {
        "total_queries": total,
        "connections": connections_count,
        "type_distribution": dict(type_stats),
        "patterns": extract_patterns(),
        "generated": datetime.now().isoformat()
    }
    return report
