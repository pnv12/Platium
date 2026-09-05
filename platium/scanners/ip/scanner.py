"""
IP Scanner — геолокація, WHOIS, проксі-детекція, Shodan (опціонально)
"""

import requests
import socket
from platium.core.result import ScanResult, ScanStatus
from platium.core.config import load_config
from platium.core.errors import NetworkError
from platium.utils.network import safe_request

def search(ip, config=None, verbose=False) -> ScanResult:
    """
    Аналізує IP-адресу: геолокація, WHOIS, проксі/VPN, Shodan (якщо є ключ).
    Повертає ScanResult з єдиним контрактом.
    """
    if config is None:
        config = load_config()

    sources = {}
    data = {}
    status = ScanStatus.NOT_FOUND
    errors = []

    # 1. Геолокація через ip-api.com (без ключа)
    try:
        resp = safe_request(f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,org,as,proxy,hosting", timeout=config.get("timeout", 10))
        if resp is None:
            sources["geo_ipapi"] = {"status": "error", "message": "No response"}
            errors.append("GeoIP: no response")
        elif resp.status_code == 200:
            data_geo = resp.json()
            if data_geo.get('status') == 'success':
                sources["geo_ipapi"] = {"status": "success", "data": data_geo}
                data["geo"] = data_geo
                status = ScanStatus.PARTIAL if status == ScanStatus.NOT_FOUND else status
            else:
                sources["geo_ipapi"] = {"status": "error", "message": data_geo.get('message', 'Unknown error')}
                errors.append(f"GeoIP: {data_geo.get('message', 'Unknown error')}")
        else:
            sources["geo_ipapi"] = {"status": "error", "code": resp.status_code, "message": "HTTP error"}
            errors.append(f"GeoIP: HTTP {resp.status_code}")
    except Exception as e:
        sources["geo_ipapi"] = {"status": "error", "message": str(e)}
        errors.append(f"GeoIP: {str(e)}")

    # 2. WHOIS (через python-whois)
    try:
        import whois
        domain_info = whois.whois(ip)
        if domain_info:
            sources["whois"] = {
                "status": "success",
                "registrar": getattr(domain_info, 'registrar', 'N/A'),
                "creation_date": str(getattr(domain_info, 'creation_date', 'N/A')),
                "expiration_date": str(getattr(domain_info, 'expiration_date', 'N/A')),
            }
            data["whois"] = sources["whois"]
            if status == ScanStatus.NOT_FOUND:
                status = ScanStatus.PARTIAL
        else:
            sources["whois"] = {"status": "not_found", "message": "WHOIS data not available"}
            errors.append("WHOIS: no data")
    except Exception as e:
        sources["whois"] = {"status": "error", "message": str(e)}
        errors.append(f"WHOIS: {str(e)}")

    # 3. Проксі/VPN детекція (на основі даних ip-api)
    if data.get("geo", {}).get("proxy") or data.get("geo", {}).get("hosting"):
        data["proxy_detected"] = {
            "proxy": data["geo"].get("proxy", False),
            "hosting": data["geo"].get("hosting", False)
        }
    else:
        data["proxy_detected"] = {"proxy": False, "hosting": False}

    # 4. Shodan (опціонально, якщо є ключ)
    shodan_key = config.get("shodan_key")
    if shodan_key:
        try:
            import shodan
            api = shodan.Shodan(shodan_key)
            host = api.host(ip)
            sources["shodan"] = {
                "status": "success",
                "ports": host.get('ports', []),
                "isp": host.get('isp', 'N/A'),
                "org": host.get('org', 'N/A')
            }
            data["shodan"] = sources["shodan"]
            if status == ScanStatus.NOT_FOUND:
                status = ScanStatus.PARTIAL
        except Exception as e:
            sources["shodan"] = {"status": "error", "message": str(e)}
            errors.append(f"Shodan: {str(e)}")
    else:
        sources["shodan"] = {"status": "skipped", "message": "No API key"}

    # Визначаємо фінальний статус
    if status == ScanStatus.NOT_FOUND and errors:
        status = ScanStatus.PARTIAL if len(errors) < len(sources) else ScanStatus.ERROR
    if status == ScanStatus.PARTIAL and not errors:
        status = ScanStatus.SUCCESS if data else ScanStatus.NOT_FOUND

    # Створюємо результат
    result = ScanResult(
        target=ip,
        scanner="ip",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.7 if status == ScanStatus.SUCCESS else 0.3,
        evidence=[f"Checked {len(sources)} sources"]
    )

    return result
