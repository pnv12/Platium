"""
IP Scanner — геолокація, Shodan, whois, проксі-детекція
"""

import aiohttp
import asyncio
import socket

async def fetch(session, url, headers=None):
    try:
        async with session.get(url, headers=headers or {}, timeout=5) as response:
            return await response.json()
    except:
        return None

async def search(ip):
    results = {}
    async with aiohttp.ClientSession() as session:
        # 1. ip-api.com
        data = await fetch(session, f"http://ip-api.com/json/{ip}")
        if data and data.get('status') == 'success':
            results["location"] = {
                "country": data.get('country', 'N/A'),
                "city": data.get('city', 'N/A'),
                "isp": data.get('isp', 'N/A'),
                "org": data.get('org', 'N/A'),
                "proxy": data.get('proxy', False)
            }
        # 2. ipinfo.io (без ключа — обмежено)
        data = await fetch(session, f"https://ipinfo.io/{ip}")
        if data and 'country' in data:
            results["location_detail"] = {
                "country": data.get('country', 'N/A'),
                "region": data.get('region', 'N/A'),
                "city": data.get('city', 'N/A'),
                "loc": data.get('loc', 'N/A'),
                "org": data.get('org', 'N/A')
            }
        # 3. Whois (синхронно, бо не має асинхронної версії)
        try:
            import whois
            domain_info = whois.whois(ip)
            results["whois"] = {
                "registrar": getattr(domain_info, 'registrar', 'N/A'),
                "creation_date": str(getattr(domain_info, 'creation_date', 'N/A')),
                "expiration_date": str(getattr(domain_info, 'expiration_date', 'N/A')),
            }
        except:
            pass
    return results
