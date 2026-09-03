"""
Deep OSINT Scanner — комбінований пошук з автовизначенням типу запиту
"""

import re
from platium.core.config import load_config
from platium.core.errors import ScannerError, ValidationError
from platium.scanners.username.scanner import search as username_search
from platium.scanners.email.scanner import search as email_search
from platium.scanners.phone.scanner import search as phone_search
from platium.scanners.ip.scanner import search as ip_search

def detect_type(query):
    """Автоматично визначає тип запиту"""
    if not query or len(query) < 2:
        return 'unknown'
    if '@' in query:
        return 'email'
    if re.match(r'^\+?\d{10,15}$', query.replace(' ', '')):
        return 'phone'
    if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', query):
        return 'ip'
    if re.match(r'^[a-zA-Z0-9_.-]+$', query):
        return 'username'
    return 'unknown'

def deep_search(query, config=None, verbose=False):
    """
    Глибокий OSINT-пошук: визначає тип і запускає релевантні сканери.
    """
    if config is None:
        config = load_config()

    result = {
        "target": query,
        "scan_type": "deep",
        "detected_type": detect_type(query),
        "results": {},
        "status": "empty"
    }

    # Маппінг типів -> сканери
    scanner_map = {
        "username": ("username", username_search),
        "email": ("email", email_search),
        "phone": ("phone", phone_search),
        "ip": ("ip", ip_search),
        "unknown": None
    }

    detected = result["detected_type"]
    if detected == "unknown":
        result["status"] = "error"
        result["error"] = "Unknown query type"
        return result

    # Запускаємо ТІЛЬКИ релевантний сканер
    scanner_info = scanner_map.get(detected)
    if scanner_info is None:
        result["status"] = "error"
        result["error"] = "Unsupported type"
        return result

    name, scanner = scanner_info
    try:
        scan_result = scanner(query, config, verbose)
        result["results"][name] = scan_result
        # Якщо сканер повернув status "success" або "found" — вважаємо це успіхом
        if scan_result.get("status") in ("success", "found", "valid"):
            result["status"] = "success"
        elif scan_result.get("status") in ("partial", "error"):
            result["status"] = "partial"
        else:
            result["status"] = "empty"
    except Exception as e:
        result["results"][name] = {"error": str(e)}
        result["status"] = "error"

    return result
