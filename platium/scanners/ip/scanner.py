import requests
import socket
from platium.core.config import config
from platium.core.result import ScanResult, ScanStatus
from platium.utils.network import safe_request

def search(ip, verbose=False):
    sources = {}
    data = {}
    status = ScanStatus.NOT_FOUND
    errors = []
    timeout = config.timeout

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,org,as,proxy,hosting"
        resp = safe_request(url, timeout=timeout)
        if resp and resp.status_code == 200:
            geo_data = resp.json()
            if geo_data.get('status') == 'success':
                sources["ip-api"] = {"status": "success", "data": geo_data}
                data["location"] = {
                    "country": geo_data.get('country'),
                    "city": geo_data.get('city'),
                    "isp": geo_data.get('isp'),
                    "org": geo_data.get('org'),
                    "as": geo_data.get('as'),
                    "proxy": geo_data.get('proxy', False),
                    "hosting": geo_data.get('hosting', False)
                }
                status = ScanStatus.SUCCESS
            else:
                sources["ip-api"] = {"status": "error", "message": geo_data.get('message', 'Unknown error')}
                errors.append("ip-api: error")
        else:
            sources["ip-api"] = {"status": "error", "code": resp.status_code if resp else 0, "message": "HTTP error"}
            errors.append(f"ip-api: HTTP {resp.status_code if resp else 'no response'}")
    except Exception as e:
        sources["ip-api"] = {"status": "error", "message": str(e)}
        errors.append(f"ip-api: {str(e)}")

    try:
        import whois
        domain_info = whois.whois(ip)
        sources["whois"] = {"status": "success", "data": {
            "registrar": getattr(domain_info, 'registrar', 'N/A'),
            "creation_date": str(getattr(domain_info, 'creation_date', 'N/A')),
            "expiration_date": str(getattr(domain_info, 'expiration_date', 'N/A')),
        }}
        data["whois"] = sources["whois"]["data"]
        if status != ScanStatus.SUCCESS:
            status = ScanStatus.PARTIAL
    except Exception as e:
        sources["whois"] = {"status": "error", "message": str(e)}
        errors.append(f"whois: {str(e)}")

    if data.get("location", {}).get("proxy"):
        data["proxy_detected"] = True
        sources["proxy"] = {"status": "success", "message": "Proxy/VPN detected"}
    else:
        data["proxy_detected"] = False
        sources["proxy"] = {"status": "not_found", "message": "No proxy/VPN detected"}

    if status == ScanStatus.NOT_FOUND and errors:
        status = ScanStatus.ERROR

    if status == ScanStatus.SUCCESS and errors:
        status = ScanStatus.PARTIAL

    shodan_key = config.get_api_key("shodan_key")
    if shodan_key:
        try:
            import shodan
            api = shodan.Shodan(shodan_key)
            host = api.host(ip)
            sources["shodan"] = {"status": "success", "data": {"ports": host.get('ports', [])}}
            data["shodan"] = {"ports": host.get('ports', [])}
            if status != ScanStatus.SUCCESS:
                status = ScanStatus.PARTIAL
        except Exception as e:
            sources["shodan"] = {"status": "error", "message": str(e)}
            errors.append(f"shodan: {str(e)}")
    else:
        sources["shodan"] = {"status": "skipped", "message": "No Shodan API key"}

    result = ScanResult(
        target=ip,
        scanner="ip",
        status=status,
        data=data,
        sources=sources,
        error="; ".join(errors) if errors else None,
        confidence=0.9 if status == ScanStatus.SUCCESS else 0.3,
        evidence=[f"Checked {len(sources)} sources"]
    )
    return result
