#!/usr/bin/env python3
"""
Deep OSINT Engine — повноцінний OSINT-сканер для Platium
Автор: Neo
Версія: 1.0
"""

import concurrent.futures
import json
import re
import socket
import subprocess
import requests
from datetime import datetime
from urllib.parse import urlparse

# Імпорт інших модулів
from modules import username_scanner, email_scanner, phone_scanner, ip_scanner
from modules import social_analyzer, darknet_scanner, graph_builder, threat_intel
from modules import report_generator
from modules.utils import print_status, animate_loading, progress_bar

# Список джерел для глибокого пошуку (без API)
DEEP_SOURCES = {
    "whois": "https://who.is/whois/{}",
    "crtsh": "https://crt.sh/?q={}",
    "shodan_demo": "https://www.shodan.io/host/{}",
    "securitytrails_demo": "https://securitytrails.com/domain/{}",
    "spyse_demo": "https://spyse.com/search/{}",
    "virustotal_demo": "https://www.virustotal.com/gui/domain/{}",
}

def deep_search(query, query_type="auto"):
    """
    Глибокий OSINT-пошук за різними типами запитів.
    query_type: auto, email, phone, ip, username, domain
    """
    results = {
        "query": query,
        "type": query_type,
        "timestamp": datetime.now().isoformat(),
        "data": {}
    }

    # Автовизначення типу запиту
    if query_type == "auto":
        if '@' in query:
            query_type = "email"
        elif re.match(r'^\+?\d{10,15}$', query.replace(' ', '')):
            query_type = "phone"
        elif re.match(r'^(\d{1,3}\.){3}\d{1,3}$', query):
            query_type = "ip"
        elif re.match(r'^[a-zA-Z0-9_.-]+$', query):
            query_type = "username"
        else:
            query_type = "domain"

    results["type"] = query_type
    print_status(f"🔍 Пошук за типом: {query_type}", "info")

    # Запуск відповідних модулів
    if query_type == "username":
        results["data"]["username"] = username_scanner.search(query)
        # Додатковий пошук email, пов'язаних з ніком
        email_hint = f"{query}@gmail.com"
        results["data"]["email_suggestions"] = [email_hint]

    elif query_type == "email":
        results["data"]["email"] = email_scanner.search(query)
        # Пошук нікнеймів, пов'язаних з email
        username_hint = query.split('@')[0]
        results["data"]["username_suggestions"] = [username_hint]

    elif query_type == "phone":
        results["data"]["phone"] = phone_scanner.search(query)

    elif query_type == "ip":
        results["data"]["ip"] = ip_scanner.search(query)
        # Додатковий whois
        try:
            import whois
            domain_info = whois.whois(query)
            results["data"]["ip_whois"] = {
                "registrar": getattr(domain_info, 'registrar', 'N/A'),
                "creation_date": str(getattr(domain_info, 'creation_date', 'N/A')),
                "expiration_date": str(getattr(domain_info, 'expiration_date', 'N/A')),
            }
        except:
            results["data"]["ip_whois"] = {"error": "WHOIS недоступний"}

    elif query_type == "domain":
        # Аналіз домену
        results["data"]["domain"] = {}
        # WHOIS
        try:
            import whois
            domain_info = whois.whois(query)
            results["data"]["domain"]["whois"] = {
                "registrar": getattr(domain_info, 'registrar', 'N/A'),
                "creation_date": str(getattr(domain_info, 'creation_date', 'N/A')),
                "expiration_date": str(getattr(domain_info, 'expiration_date', 'N/A')),
                "name_servers": getattr(domain_info, 'name_servers', []),
            }
        except:
            results["data"]["domain"]["whois"] = {"error": "WHOIS недоступний"}

        # Пошук піддоменів через crt.sh
        try:
            response = requests.get(f"https://crt.sh/?q={query}", timeout=10)
            if response.status_code == 200:
                subdomains = re.findall(r'<TD>([a-zA-Z0-9.-]+\.{})</TD>'.format(query.replace('.', '\.')), response.text)
                results["data"]["domain"]["subdomains"] = list(set(subdomains))[:20]  # максимум 20
            else:
                results["data"]["domain"]["subdomains"] = []
        except:
            results["data"]["domain"]["subdomains"] = []

        # Пошук email на сайті (простий парсинг)
        try:
            response = requests.get(f"http://{query}", timeout=5)
            emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', response.text)
            results["data"]["domain"]["emails"] = list(set(emails))[:10]
        except:
            results["data"]["domain"]["emails"] = []

    # Граф зв'язків (якщо є email або номер)
    if query_type in ["email", "phone", "username"]:
        try:
            graph_data = graph_builder.build(query)
            results["data"]["graph"] = graph_data
        except:
            results["data"]["graph"] = {"error": "Граф зв'язків недоступний"}

    # Threat Intelligence (якщо є IP або домен)
    if query_type in ["ip", "domain"]:
        try:
            threat_data = threat_intel.check(query)
            results["data"]["threat"] = threat_data
        except:
            results["data"]["threat"] = {"error": "Threat Intelligence недоступний"}

    # Соціальний аналіз (якщо є нік)
    if query_type == "username":
        try:
            social_data = social_analyzer.search(query)
            results["data"]["social"] = social_data
        except:
            results["data"]["social"] = {"error": "Соціальний аналіз недоступний"}

    # Даркнет-пошук (якщо є нік, email або IP)
    if query_type in ["username", "email", "ip"]:
        try:
            darknet_data = darknet_scanner.search(query)
            results["data"]["darknet"] = darknet_data
        except:
            results["data"]["darknet"] = {"error": "Даркнет-пошук недоступний"}

    # Генерація звіту
    report_path = f"data/reports/deep_osint_{query.replace('@', '_').replace('.', '_')}.txt"
    report_generator.generate(results, report_path)

    return results

def run_deep_osint_cli():
    """CLI-інтерфейс для Deep OSINT"""
    import argparse

    parser = argparse.ArgumentParser(description="Deep OSINT Engine")
    parser.add_argument("-q", "--query", required=True, help="Запит для пошуку (email, номер, IP, нік, домен)")
    parser.add_argument("-t", "--type", default="auto", choices=["auto", "email", "phone", "ip", "username", "domain"], help="Тип запиту")
    parser.add_argument("-o", "--output", help="Шлях для збереження звіту")
    args = parser.parse_args()

    results = deep_search(args.query, args.type)

    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТИ ГЛИБОКОГО OSINT:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    print("="*60)

if __name__ == "__main__":
    run_deep_osint_cli()
