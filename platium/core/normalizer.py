"""
Normalizer — обов'язковий шар для перетворення ScanResult у структуровані сутності.
Використовується в усіх сканерах перед збереженням у базу даних.
"""

import re
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
from platium.core.result import ScanResult, ScanStatus
from platium.core.paths import DB_PATH
from platium.intelligence.aggregator import (
    _get_or_create_entity,
    save_observation,
    save_relationship
)

class Normalizer:
    """
    Нормалізує ScanResult у набір сутностей, спостережень та зв'язків.
    """
    
    @staticmethod
    def normalize(result: ScanResult) -> Dict[str, Any]:
        """
        Головний метод нормалізації.
        Повертає словник з нормалізованими даними.
        """
        if not result or not result.target:
            return {"error": "Invalid result"}

        # Визначаємо тип сутності
        entity_type = Normalizer._infer_entity_type(result.scanner, result.target)
        
        # Створюємо або отримуємо сутність
        entity_id = _get_or_create_entity(entity_type, result.target)
        
        # Нормалізуємо спостереження
        observations = Normalizer._normalize_observations(result, entity_id)
        
        # Нормалізуємо зв'язки
        relationships = Normalizer._normalize_relationships(result, entity_id)
        
        # Додаткові метадані
        metadata = {
            "normalized_at": datetime.now().isoformat(),
            "scanner": result.scanner,
            "status": result.status.value,
            "confidence": result.confidence,
            "evidence": result.evidence,
            "error": result.error
        }
        
        return {
            "entity_id": entity_id,
            "entity_type": entity_type,
            "target": result.target,
            "observations": observations,
            "relationships": relationships,
            "metadata": metadata
        }

    @staticmethod
    def _infer_entity_type(scanner: str, target: str) -> str:
        """Визначає тип сутності на основі сканера та цілі."""
        mapping = {
            "email": "email" if "@" in target else "unknown",
            "username": "username",
            "phone": "phone",
            "ip": "ip",
            "exif": "image",
            "social": "username",
            "threat": "ip",
            "graph": "username",
            "darknet": "domain",
            "deep": "auto"
        }
        return mapping.get(scanner, "unknown")

    @staticmethod
    def _normalize_observations(result: ScanResult, entity_id: int) -> List[Dict]:
        """Нормалізує спостереження з результату."""
        observations = []
        
        for source, source_data in result.sources.items():
            status_str = source_data.get("status", "unknown")
            confidence = source_data.get("confidence", result.confidence)
            
            observation = {
                "entity_id": entity_id,
                "scanner": result.scanner,
                "source": source,
                "status": status_str,
                "data": source_data.get("data") or source_data,
                "confidence": confidence,
                "evidence": source_data.get("evidence") or result.evidence
            }
            observations.append(observation)
            
            # Зберігаємо в базу даних
            save_observation(
                entity_id=entity_id,
                scanner=result.scanner,
                source=source,
                status=status_str,
                data=observation["data"],
                confidence=confidence,
                evidence=observation["evidence"]
            )
        
        return observations

    @staticmethod
    def _normalize_relationships(result: ScanResult, entity_id: int) -> List[Dict]:
        """Нормалізує зв'язки з результату."""
        relationships = []
        
        # Якщо є дані, шукаємо зв'язки
        if result.data:
            data = result.data
            
            # Для email сканера
            if result.scanner == "email" and "hibp" in data:
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
                        relationships.append({
                            "source": entity_id,
                            "target": breach_entity_id,
                            "relation": "appears_in_breach",
                            "confidence": 0.9,
                            "evidence": f"Found in {breach}"
                        })
            
            # Для username сканера
            if result.scanner == "username":
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
                        relationships.append({
                            "source": entity_id,
                            "target": platform_entity_id,
                            "relation": "has_profile_on",
                            "confidence": 0.9,
                            "evidence": info.get("url", "")
                        })
            
            # Для phone сканера
            if result.scanner == "phone":
                phone_data = data.get("data", {})
                if phone_data.get("country"):
                    country = phone_data["country"]
                    country_entity_id = _get_or_create_entity("country", country)
                    save_relationship(
                        source_entity_id=entity_id,
                        target_entity_id=country_entity_id,
                        relation_type="located_in",
                        confidence=0.9,
                        evidence=f"Phone registered in {country}"
                    )
                    relationships.append({
                        "source": entity_id,
                        "target": country_entity_id,
                        "relation": "located_in",
                        "confidence": 0.9,
                        "evidence": f"Phone registered in {country}"
                    })
                if phone_data.get("operator"):
                    operator = phone_data["operator"]
                    operator_entity_id = _get_or_create_entity("operator", operator)
                    save_relationship(
                        source_entity_id=entity_id,
                        target_entity_id=operator_entity_id,
                        relation_type="uses_operator",
                        confidence=0.9,
                        evidence=f"Phone uses {operator}"
                    )
                    relationships.append({
                        "source": entity_id,
                        "target": operator_entity_id,
                        "relation": "uses_operator",
                        "confidence": 0.9,
                        "evidence": f"Phone uses {operator}"
                    })
            
            # Для ip сканера
            if result.scanner == "ip":
                location = data.get("location", {})
                if location.get("country"):
                    country = location["country"]
                    country_entity_id = _get_or_create_entity("country", country)
                    save_relationship(
                        source_entity_id=entity_id,
                        target_entity_id=country_entity_id,
                        relation_type="located_in",
                        confidence=0.85,
                        evidence=f"IP located in {country}"
                    )
                    relationships.append({
                        "source": entity_id,
                        "target": country_entity_id,
                        "relation": "located_in",
                        "confidence": 0.85,
                        "evidence": f"IP located in {country}"
                    })
            
            # Для exif сканера
            if result.scanner == "exif":
                # Якщо є GPS координати, створюємо гео-сутність
                if "GPSInfo" in data:
                    gps_data = data["GPSInfo"]
                    # Спрощена обробка GPS
                    lat = gps_data.get("GPSLatitude")
                    lon = gps_data.get("GPSLongitude")
                    if lat and lon:
                        location_str = f"{lat},{lon}"
                        location_entity_id = _get_or_create_entity("location", location_str)
                        save_relationship(
                            source_entity_id=entity_id,
                            target_entity_id=location_entity_id,
                            relation_type="photo_taken_at",
                            confidence=0.9,
                            evidence=f"GPS coordinates: {location_str}"
                        )
                        relationships.append({
                            "source": entity_id,
                            "target": location_entity_id,
                            "relation": "photo_taken_at",
                            "confidence": 0.9,
                            "evidence": f"GPS coordinates: {location_str}"
                        })
        
        return relationships


def normalize_result(result: ScanResult) -> Dict[str, Any]:
    """
    Зручна функція для виклику нормалізації з CLI або інших модулів.
    """
    return Normalizer.normalize(result)


def store_normalized_result(result: ScanResult) -> int:
    """
    Нормалізує результат і зберігає його в базу даних.
    Повертає ID сутності.
    """
    normalized = Normalizer.normalize(result)
    return normalized["entity_id"]
