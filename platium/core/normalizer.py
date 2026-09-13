"""
Normalizer — обов'язковий шар для перетворення ScanResult у структуровані сутності.
Використовується в усіх сканерах перед збереженням у базу даних.
"""

from datetime import datetime
from typing import Dict, Any, List

from platium.core.result import ScanResult
from platium.storage.database import (
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

        entity_type = Normalizer._infer_entity_type(
            result.scanner,
            result.target
        )

        entity_id = _get_or_create_entity(
            entity_type,
            result.target
        )

        observations = Normalizer._normalize_observations(
            result,
            entity_id
        )

        relationships = Normalizer._normalize_relationships(
            result,
            entity_id
        )

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
            "image": "image",
            "social": "username",
            "threat": "ip",
            "graph": "username",
            "darknet": "domain",
            "deep": "auto"
        }

        return mapping.get(scanner, "unknown")

    @staticmethod
    def _normalize_observations(
        result: ScanResult,
        entity_id: int
    ) -> List[Dict]:
        """Нормалізує спостереження з результату."""
        observations = []

        for source, source_data in result.sources.items():
            status_str = source_data.get(
                "status",
                "unknown"
            )

            confidence = source_data.get(
                "confidence",
                result.confidence
            )

            observation = {
                "entity_id": entity_id,
                "scanner": result.scanner,
                "source": source,
                "status": status_str,
                "data": source_data.get("data") or source_data,
                "confidence": confidence,
                "evidence": source_data.get(
                    "evidence"
                ) or result.evidence
            }

            observations.append(observation)

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
    def _normalize_relationships(
        result: ScanResult,
        entity_id: int
    ) -> List[Dict]:
        """Нормалізує зв'язки з результату."""
        relationships = []

        if not result.data:
            return relationships

        data = result.data

        if result.scanner == "email" and "hibp" in data:
            breaches = data.get("hibp", [])

            if isinstance(breaches, list):
                for breach in breaches:
                    breach_entity_id = _get_or_create_entity(
                        "breach",
                        breach
                    )

                    evidence = f"Found in {breach}"

                    save_relationship(
                        source_entity_id=entity_id,
                        target_entity_id=breach_entity_id,
                        relation_type="appears_in_breach",
                        confidence=0.9,
                        evidence=evidence
                    )

                    relationships.append({
                        "source": entity_id,
                        "target": breach_entity_id,
                        "relation": "appears_in_breach",
                        "confidence": 0.9,
                        "evidence": evidence
                    })

        if result.scanner == "username":
            for platform, info in data.items():
                if (
                    isinstance(info, dict)
                    and info.get("status") == "found"
                ):
                    platform_entity_id = _get_or_create_entity(
                        "platform",
                        platform
                    )

                    evidence = info.get("url", "")

                    save_relationship(
                        source_entity_id=entity_id,
                        target_entity_id=platform_entity_id,
                        relation_type="has_profile_on",
                        confidence=0.9,
                        evidence=evidence
                    )

                    relationships.append({
                        "source": entity_id,
                        "target": platform_entity_id,
                        "relation": "has_profile_on",
                        "confidence": 0.9,
                        "evidence": evidence
                    })

        if result.scanner == "phone":
            phone_data = data.get("data", {})

            if phone_data.get("country"):
                country = phone_data["country"]

                country_entity_id = _get_or_create_entity(
                    "country",
                    country
                )

                evidence = f"Phone registered in {country}"

                save_relationship(
                    source_entity_id=entity_id,
                    target_entity_id=country_entity_id,
                    relation_type="located_in",
                    confidence=0.9,
                    evidence=evidence
                )

                relationships.append({
                    "source": entity_id,
                    "target": country_entity_id,
                    "relation": "located_in",
                    "confidence": 0.9,
                    "evidence": evidence
                })

            if phone_data.get("operator"):
                operator = phone_data["operator"]

                operator_entity_id = _get_or_create_entity(
                    "operator",
                    operator
                )

                evidence = f"Phone uses {operator}"

                save_relationship(
                    source_entity_id=entity_id,
                    target_entity_id=operator_entity_id,
                    relation_type="uses_operator",
                    confidence=0.9,
                    evidence=evidence
                )

                relationships.append({
                    "source": entity_id,
                    "target": operator_entity_id,
                    "relation": "uses_operator",
                    "confidence": 0.9,
                    "evidence": evidence
                })

        if result.scanner == "ip":
            location = data.get("location", {})

            if location.get("country"):
                country = location["country"]

                country_entity_id = _get_or_create_entity(
                    "country",
                    country
                )

                evidence = f"IP located in {country}"

                save_relationship(
                    source_entity_id=entity_id,
                    target_entity_id=country_entity_id,
                    relation_type="located_in",
                    confidence=0.85,
                    evidence=evidence
                )

                relationships.append({
                    "source": entity_id,
                    "target": country_entity_id,
                    "relation": "located_in",
                    "confidence": 0.85,
                    "evidence": evidence
                })

        if result.scanner == "exif":
            if "GPSInfo" in data:
                gps_data = data["GPSInfo"]

                if isinstance(gps_data, dict):
                    lat = gps_data.get("GPSLatitude")
                    lon = gps_data.get("GPSLongitude")

                    if lat and lon:
                        location_str = f"{lat},{lon}"

                        location_entity_id = _get_or_create_entity(
                            "location",
                            location_str
                        )

                        evidence = (
                            f"GPS coordinates: {location_str}"
                        )

                        save_relationship(
                            source_entity_id=entity_id,
                            target_entity_id=location_entity_id,
                            relation_type="photo_taken_at",
                            confidence=0.9,
                            evidence=evidence
                        )

                        relationships.append({
                            "source": entity_id,
                            "target": location_entity_id,
                            "relation": "photo_taken_at",
                            "confidence": 0.9,
                            "evidence": evidence
                        })

        if result.scanner == "image":
            fingerprint_data = data.get(
                "fingerprint",
                {}
            )

            sha256 = fingerprint_data.get("sha256")

            if sha256:
                hash_entity_id = _get_or_create_entity(
                    "image_sha256",
                    sha256
                )

                evidence = f"SHA-256: {sha256}"

                save_relationship(
                    source_entity_id=entity_id,
                    target_entity_id=hash_entity_id,
                    relation_type="has_sha256",
                    confidence=1.0,
                    evidence=evidence
                )

                relationships.append({
                    "source": entity_id,
                    "target": hash_entity_id,
                    "relation": "has_sha256",
                    "confidence": 1.0,
                    "evidence": evidence
                })

            average_hash = fingerprint_data.get(
                "average_hash"
            )

            if average_hash:
                phash_entity_id = _get_or_create_entity(
                    "image_perceptual_hash",
                    average_hash
                )

                evidence = (
                    "Perceptual average hash calculated"
                )

                save_relationship(
                    source_entity_id=entity_id,
                    target_entity_id=phash_entity_id,
                    relation_type="has_perceptual_hash",
                    confidence=0.95,
                    evidence=evidence
                )

                relationships.append({
                    "source": entity_id,
                    "target": phash_entity_id,
                    "relation": "has_perceptual_hash",
                    "confidence": 0.95,
                    "evidence": evidence
                })

            metadata = data.get("metadata", {})
            exif = metadata.get("exif", {})
            exif_fields = exif.get("fields", {})

            if isinstance(exif_fields, dict):
                entity_fields = {
                    "Make": "camera_make",
                    "Model": "camera_model",
                    "Software": "software",
                    "DateTime": "datetime_original",
                    "DateTimeOriginal": "datetime_original",
                    "DateTimeDigitized": "datetime_digitized"
                }

                relation_types = {
                    "camera_make": "captured_with_make",
                    "camera_model": "captured_with_model",
                    "software": "processed_with",
                    "datetime_original": "captured_at",
                    "datetime_digitized": "digitized_at"
                }

                for field_name, entity_type in entity_fields.items():
                    value = exif_fields.get(field_name)

                    if not value:
                        continue

                    metadata_entity_id = _get_or_create_entity(
                        entity_type,
                        value
                    )

                    relation_type = relation_types[entity_type]

                    evidence = (
                        f"EXIF {field_name}: {value}"
                    )

                    save_relationship(
                        source_entity_id=entity_id,
                        target_entity_id=metadata_entity_id,
                        relation_type=relation_type,
                        confidence=0.9,
                        evidence=evidence
                    )

                    relationships.append({
                        "source": entity_id,
                        "target": metadata_entity_id,
                        "relation": relation_type,
                        "confidence": 0.9,
                        "evidence": evidence
                    })

            gps = exif.get("gps", {})

            if isinstance(gps, dict) and gps.get("present"):
                gps_entity_id = _get_or_create_entity(
                    "gps_metadata",
                    "present"
                )

                evidence = (
                    "EXIF GPS metadata is present"
                )

                save_relationship(
                    source_entity_id=entity_id,
                    target_entity_id=gps_entity_id,
                    relation_type="contains_gps_metadata",
                    confidence=0.95,
                    evidence=evidence
                )

                relationships.append({
                    "source": entity_id,
                    "target": gps_entity_id,
                    "relation": "contains_gps_metadata",
                    "confidence": 0.95,
                    "evidence": evidence
                })

                latitude = gps.get("latitude")
                longitude = gps.get("longitude")

                if latitude is not None and longitude is not None:
                    location_str = (
                        f"{latitude:.8f},{longitude:.8f}"
                    )

                    location_entity_id = _get_or_create_entity(
                        "location",
                        location_str
                    )

                    evidence = (
                        f"GPS coordinates: {location_str}"
                    )

                    save_relationship(
                        source_entity_id=entity_id,
                        target_entity_id=location_entity_id,
                        relation_type="photo_taken_at",
                        confidence=0.98,
                        evidence=evidence
                    )

                    relationships.append({
                        "source": entity_id,
                        "target": location_entity_id,
                        "relation": "photo_taken_at",
                        "confidence": 0.98,
                        "evidence": evidence
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
