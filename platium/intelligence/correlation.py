"""
Correlation Engine — пошук зв'язків між сутностями
"""

import sqlite3
import json
from platium.intelligence.aggregator import DB_PATH, _get_or_create_entity, save_relationship

class CorrelationEngine:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def close(self):
        self.conn.close()

    def get_all_entities(self):
        """Отримує всі сутності з бази"""
        self.cursor.execute("SELECT id, entity_type, value FROM entities")
        return self.cursor.fetchall()

    def find_connections(self):
        """
        Шукає зв'язки між сутностями на основі спільних атрибутів.
        Повертає список знайдених зв'язків.
        """
        entities = self.get_all_entities()
        relationships = []

        # Групуємо сутності за типами
        by_type = {}
        for entity_id, entity_type, value in entities:
            if entity_type not in by_type:
                by_type[entity_type] = []
            by_type[entity_type].append((entity_id, value))

        # 1. Зв'язки між email та username (якщо username є частиною email)
        if "email" in by_type and "username" in by_type:
            for email_id, email_value in by_type["email"]:
                # Витягуємо локальну частину email
                local_part = email_value.split('@')[0].lower()
                for username_id, username_value in by_type["username"]:
                    if username_value.lower() == local_part:
                        relationships.append({
                            "source_id": email_id,
                            "target_id": username_id,
                            "relation_type": "email_username_match",
                            "confidence": 0.8,
                            "evidence": f"Local part '{local_part}' matches username '{username_value}'"
                        })

        # 2. Зв'язки між email та доменами
        if "email" in by_type:
            for email_id, email_value in by_type["email"]:
                domain = email_value.split('@')[1].lower()
                # Шукаємо домен як сутність
                self.cursor.execute("SELECT id FROM entities WHERE entity_type = 'domain' AND value = ?", (domain,))
                row = self.cursor.fetchone()
                if row:
                    domain_id = row[0]
                    relationships.append({
                        "source_id": email_id,
                        "target_id": domain_id,
                        "relation_type": "uses_domain",
                        "confidence": 0.9,
                        "evidence": f"Email uses domain '{domain}'"
                    })

        # 3. Зв'язки між IP та країнами/операторами (вже зберігаються в aggregator)
        # Додатково: зв'язки між IP та доменами (якщо є)
        if "ip" in by_type and "domain" in by_type:
            for ip_id, ip_value in by_type["ip"]:
                # Шукаємо домени, які резолв'яться на цей IP
                # (поки що заглушка, можна додати реальний DNS-запит пізніше)
                pass

        # 4. Зв'язки між phone та операторами (вже зберігаються)

        return relationships

    def save_relationships(self, relationships):
        """Зберігає знайдені зв'язки в базу"""
        for rel in relationships:
            save_relationship(
                source_entity_id=rel["source_id"],
                target_entity_id=rel["target_id"],
                relation_type=rel["relation_type"],
                confidence=rel["confidence"],
                evidence=rel["evidence"]
            )

    def run_correlation(self):
        """Запускає повний цикл кореляції"""
        print("[+] Starting correlation...")
        relationships = self.find_connections()
        if relationships:
            self.save_relationships(relationships)
            print(f"[+] Saved {len(relationships)} relationships")
        else:
            print("[+] No new relationships found")
        return relationships

def run_full_correlation():
    """Функція для запуску кореляції з CLI"""
    engine = CorrelationEngine()
    try:
        relationships = engine.run_correlation()
        return relationships
    finally:
        engine.close()
