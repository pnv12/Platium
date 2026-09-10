"""
Correlation Engine — пошук зв'язків між сутностями.
Працює через Storage API та не залежить від Aggregator.
"""

from platium.storage.database import (
    list_entities,
    get_entity_by_value,
    get_relationships,
    save_relationship
)


class CorrelationEngine:
    def __init__(self):
        pass

    def close(self):
        pass

    def get_all_entities(self):
        """Отримує всі сутності через Storage API."""
        return list_entities(limit=1000000)

    def find_connections(self):
        """
        Шукає зв'язки між сутностями на основі відомих ознак.

        Повертає тільки зв'язки, які ще не були збережені.
        """
        entities = self.get_all_entities()
        relationships = []

        by_type = {}

        for entity in entities:
            entity_type = entity["entity_type"]

            if entity_type not in by_type:
                by_type[entity_type] = []

            by_type[entity_type].append(
                (entity["id"], entity["value"])
            )

        existing_keys = set()

        for entity in entities:
            entity_relationships = get_relationships(
                entity["id"],
                direction="outgoing"
            )

            for relationship in entity_relationships:
                existing_keys.add((
                    relationship["source_entity_id"],
                    relationship["target_entity_id"],
                    relationship["relation_type"]
                ))

        # 1. Email ↔ username
        if "email" in by_type and "username" in by_type:
            for email_id, email_value in by_type["email"]:
                if "@" not in email_value:
                    continue

                local_part = email_value.split("@", 1)[0].lower()

                for username_id, username_value in by_type["username"]:
                    if username_value.lower() != local_part:
                        continue

                    key = (
                        email_id,
                        username_id,
                        "email_username_match"
                    )

                    if key in existing_keys:
                        continue

                    relationships.append({
                        "source_id": email_id,
                        "target_id": username_id,
                        "relation_type": "email_username_match",
                        "confidence": 0.8,
                        "evidence": (
                            f"Local part '{local_part}' matches "
                            f"username '{username_value}'"
                        )
                    })

        # 2. Email → domain
        if "email" in by_type and "domain" in by_type:
            domain_ids = {
                value.lower(): entity_id
                for entity_id, value in by_type["domain"]
            }

            for email_id, email_value in by_type["email"]:
                if "@" not in email_value:
                    continue

                domain = email_value.split("@", 1)[1].lower()
                domain_id = domain_ids.get(domain)

                if domain_id is None:
                    continue

                key = (
                    email_id,
                    domain_id,
                    "uses_domain"
                )

                if key in existing_keys:
                    continue

                relationships.append({
                    "source_id": email_id,
                    "target_id": domain_id,
                    "relation_type": "uses_domain",
                    "confidence": 0.9,
                    "evidence": f"Email uses domain '{domain}'"
                })

        # 3. IP → domain
        #
        # Реальний DNS correlation буде доданий окремим модулем.
        # Тут навмисно не виконуємо мережеві запити.
        #
        # 4. Phone → operator/country
        #
        # Ці зв'язки вже створюються Normalizer.
        # Correlation не дублює їх.

        return relationships

    def save_relationships(self, relationships):
        """Зберігає знайдені зв'язки через Storage API."""
        saved = 0

        for relationship in relationships:
            save_relationship(
                source_entity_id=relationship["source_id"],
                target_entity_id=relationship["target_id"],
                relation_type=relationship["relation_type"],
                confidence=relationship["confidence"],
                evidence=relationship["evidence"]
            )

            saved += 1

        return saved

    def run_correlation(self):
        """Запускає повний цикл кореляції."""
        print("[+] Starting correlation...")

        relationships = self.find_connections()

        if relationships:
            saved = self.save_relationships(relationships)
            print(
                f"[+] Saved {saved} new relationships"
            )
        else:
            print("[+] No new relationships found")

        return relationships


def run_full_correlation():
    """Функція для запуску кореляції з CLI."""
    engine = CorrelationEngine()

    try:
        return engine.run_correlation()
    finally:
        engine.close()
