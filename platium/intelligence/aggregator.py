"""
Aggregation Layer — агрегація нормалізованих intelligence-даних.

Відповідальність:
- приймати ScanResult і передавати його в Normalizer;
- отримувати збережені зв'язки через Storage API;
- формувати зведену статистику intelligence-бази.

Aggregator не працює з SQL напряму.
"""

from datetime import datetime

from platium.core.result import ScanResult
from platium.core.normalizer import normalize_result
from platium.storage.database import (
    get_entity_by_value,
    get_relationships,
    get_database_stats,
)


def store_scan_result(result: ScanResult):
    """
    Нормалізує та зберігає результат сканування.

    Повертає ID головної сутності.
    """
    if not isinstance(result, ScanResult):
        raise TypeError("result must be a ScanResult")

    normalized = normalize_result(result)

    if "error" in normalized:
        raise ValueError(normalized["error"])

    return normalized["entity_id"]


def find_connections(entity_value):
    """
    Повертає збережені вихідні зв'язки сутності.

    Пошук виконується через Storage API.
    """
    entity = get_entity_by_value(entity_value)

    if not entity:
        return []

    relationships = get_relationships(
        entity["id"],
        direction="outgoing"
    )

    connections = []

    for relationship in relationships:
        entity_data = relationship.get("entity", {})

        connections.append({
            "target": entity_data.get("value"),
            "relation": relationship.get("relation_type"),
            "confidence": relationship.get("confidence"),
            "evidence": relationship.get("evidence")
        })

    return connections


def get_entity_connections(entity_value):
    """
    Повертає повну картину зв'язків сутності:
    outgoing + incoming.
    """
    entity = get_entity_by_value(entity_value)

    if not entity:
        return []

    relationships = get_relationships(
        entity["id"],
        direction="both"
    )

    connections = []

    for relationship in relationships:
        source = relationship.get("source", {})
        target = relationship.get("target", {})

        if relationship["source_entity_id"] == entity["id"]:
            direction = "outgoing"
            related_entity = target
        else:
            direction = "incoming"
            related_entity = source

        connections.append({
            "entity": related_entity,
            "direction": direction,
            "relation": relationship.get("relation_type"),
            "confidence": relationship.get("confidence"),
            "evidence": relationship.get("evidence"),
            "timestamp": relationship.get("timestamp")
        })

    return connections


def generate_analysis_report():
    """
    Формує зведений звіт про поточний стан intelligence-бази.

    Статистика отримується через Storage API.
    """
    stats = get_database_stats()

    return {
        "entities": stats["entities"],
        "observations": stats["observations"],
        "relationships": stats["relationships"],
        "type_distribution": stats["type_distribution"],
        "generated": datetime.now().isoformat()
    }


def aggregate_entity(entity_value):
    """
    Формує агреговане представлення однієї сутності.

    Включає саму сутність та всі її зв'язки.
    """
    entity = get_entity_by_value(entity_value)

    if not entity:
        return None

    return {
        "entity": entity,
        "connections": get_entity_connections(entity_value)
    }
