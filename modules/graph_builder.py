"""
Graph Builder — побудова графу зв'язків (SecurityTrails + Spyse)
"""

import aiohttp
import asyncio
from config import SECURITYTRAILS_API_KEY

async def fetch(session, url, headers=None):
    try:
        async with session.get(url, headers=headers or {}, timeout=10) as response:
            if response.status == 200:
                return await response.json()
            else:
                return None
    except:
        return None

async def build(email):
    results = {"connections": [], "links": 0}
    
    # 1. SecurityTrails (з ключем)
    if SECURITYTRAILS_API_KEY:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.securitytrails.com/v1/email/{email}"
            headers = {"APIKEY": SECURITYTRAILS_API_KEY}
            data = await fetch(session, url, headers)
            if data and isinstance(data, dict):
                # Приклад: дані про зв'язки
                results["securitytrails"] = data
    else:
        results["securitytrails"] = {"error": "Ключ не знайдено"}
    
    # 2. Spyse (демо, без ключа)
    results["spyse"] = {"note": "Отримайте ключ для реального аналізу"}
    
    # 3. Локальна заглушка (на випадок, якщо немає ключів)
    results["connections"] = ["pnv21", "neo", "saturn"]
    results["links"] = 3
    
    return results
