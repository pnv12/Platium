"""
Darknet Scanner — пошук у даркнеті через Ahmia + Tor
"""

import requests
from bs4 import BeautifulSoup

def search(query):
    """Пошук .onion сайтів через Ahmia (з Tor)"""
    results = {}
    
    # Налаштування проксі, якщо Tor запущено
    proxies = {
        'http': 'socks5h://127.0.0.1:9050',
        'https': 'socks5h://127.0.0.1:9050'
    } if check_tor() else {}
    
    try:
        url = f"https://ahmia.fi/search/?q={query}"
        response = requests.get(url, proxies=proxies, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            onion_links = [a['href'] for a in links if '.onion' in a['href']]
            results["results"] = onion_links[:10]  # максимум 10 посилань
            results["source"] = "ahmia.fi"
        else:
            results["error"] = "Помилка підключення до Ahmia"
    except Exception as e:
        results["error"] = str(e)
    
    return results

def check_tor():
    """Перевіряє, чи запущено Tor"""
    try:
        requests.get('http://127.0.0.1:9050', timeout=1)
        return True
    except:
        return False
