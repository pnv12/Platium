"""
Deep OSINT Scanner — комбінований пошук за будь-яким типом запиту
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
    Глибокий OSINT-пошук: визначає тип запиту і запускає всі відповідні сканери
    """
    if config is None:
        config = load_config()
    
    result = {
        "target": query,
        "scan_type": "deep",
        "detected_type": detect_type(query),
        "results": {},
        "status": "partial"
    }
    
    # Запускаємо всі можливі сканери
    scanners = {
        "username": username_search,
        "email": email_search,
        "phone": phone_search,
        "ip": ip_search
    }
    
    for name, scanner in scanners.items():
        try:
            if name == "username" and not re.match(r'^[a-zA-Z0-9_.-]+$', query):
                continue
            if name == "email" and '@' not in query:
                continue
            if name == "phone" and not re.match(r'^\+?\d{10,15}$', query.replace(' ', '')):
                continue
            if name == "ip" and not re.match(r'^(\d{1,3}\.){3}\d{1,3}$', query):
                continue
                
            scan_result = scanner(query, config, verbose)
            result["results"][name] = scan_result
        except Exception as e:
            result["results"][name] = {"error": str(e)}
    
    # Якщо хоч щось знайдено — статус success
    if any(r.get('status') == 'found' or r.get('status') == 'valid' for r in result["results"].values() if isinstance(r, dict)):
        result["status"] = "success"
    elif result["results"]:
        result["status"] = "partial"
    else:
        result["status"] = "empty"
    
    return result
