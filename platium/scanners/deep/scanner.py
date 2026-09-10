"""
Deep OSINT Scanner — комбінований пошук з автовизначенням типу запиту.
"""

import re

from platium.core.config import load_config
from platium.core.errors import ScannerError, ValidationError
from platium.core.result import ScanResult, ScanStatus
from platium.scanners.username.scanner import search as username_search
from platium.scanners.email.scanner import search as email_search
from platium.scanners.phone.scanner import search as phone_search
from platium.scanners.ip.scanner import search as ip_search


def detect_type(query):
    """Автоматично визначає тип запиту."""
    if not query or len(query) < 2:
        return "unknown"

    if "@" in query:
        return "email"

    if re.match(r"^\+?\d{10,15}$", query.replace(" ", "")):
        return "phone"

    if re.match(r"^(\d{1,3}\.){3}\d{1,3}$", query):
        return "ip"

    if re.match(r"^[a-zA-Z0-9_.-]+$", query):
        return "username"

    return "unknown"


def deep_search(query, config=None, verbose=False) -> ScanResult:
    """
    Глибокий OSINT-пошук: визначає тип і запускає релевантний сканер.

    Повертає єдиний ScanResult для сумісності з іншими сканерами Platium.
    """
    if config is None:
        config = load_config()

    detected = detect_type(query)

    if detected == "unknown":
        return ScanResult.error_result(
            target=query,
            scanner="deep",
            error="Unknown query type"
        )

    scanner_map = {
        "username": username_search,
        "email": email_search,
        "phone": phone_search,
        "ip": ip_search,
    }

    scanner = scanner_map.get(detected)

    if scanner is None:
        return ScanResult.error_result(
            target=query,
            scanner="deep",
            error="Unsupported type"
        )

    try:
        scan_result = scanner(
            query,
            config,
            verbose
        )

        result_data = {
            "detected_type": detected,
            "results": {
                detected: scan_result.to_dict()
            }
        }

        if scan_result.status == ScanStatus.SUCCESS:
            status = ScanStatus.SUCCESS
        elif scan_result.status in (
            ScanStatus.ERROR,
            ScanStatus.PARTIAL
        ):
            status = ScanStatus.PARTIAL
        else:
            status = ScanStatus.NOT_FOUND

        return ScanResult(
            target=query,
            scanner="deep",
            status=status,
            data=result_data,
            sources={
                detected: {
                    "status": scan_result.status.value,
                    "confidence": scan_result.confidence
                }
            },
            error=scan_result.error,
            confidence=scan_result.confidence,
            evidence=scan_result.evidence
        )

    except (ValidationError, ScannerError) as exc:
        return ScanResult.error_result(
            target=query,
            scanner="deep",
            error=str(exc)
        )

    except Exception as exc:
        return ScanResult.error_result(
            target=query,
            scanner="deep",
            error=str(exc)
        )
