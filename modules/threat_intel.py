"""
Threat Intelligence — VirusTotal, AbuseIPDB, Shodan
"""

import aiohttp
import asyncio
from config import VIRUSTOTAL_API_KEY, ABUSEIPDB_API_KEY, SHODAN_API_KEY

async def fetch(session, url, headers=None):
    try:
        async with session.get(url, headers=headers or {}, timeout=10) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None
    except:
        return None

async def check(query):
    results = {}
    async with aiohttp.ClientSession() as session:
        # 1. VirusTotal
        if VIRUSTOTAL_API_KEY:
            url = f"https://www.virustotal.com/api/v3/ip_addresses/{query}"
            headers = {"x-apikey": VIRUSTOTAL_API_KEY}
            data = await fetch(session, url, headers)
            if data:
                results["virustotal"] = data
        else:
            results["virustotal"] = {"error": "Ключ не знайдено"}
        
        # 2. AbuseIPDB
        if ABUSEIPDB_API_KEY:
            url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={query}"
            headers = {"Key": ABUSEIPDB_API_KEY, "Accept": "application/json"}
            data = await fetch(session, url, headers)
            if data:
                results["abuseipdb"] = data
        else:
            results["abuseipdb"] = {"error": "Ключ не знайдено"}
        
        # 3. Shodan
        if SHODAN_API_KEY:
            try:
                import shodan
                api = shodan.Shodan(SHODAN_API_KEY)
                host = api.host(query)
                results["shodan"] = {"ports": host.get('ports', [])}
            except:
                results["shodan"] = {"error": "Помилка Shodan"}
        else:
            results["shodan"] = {"error": "Ключ не знайдено"}
    
    return results
