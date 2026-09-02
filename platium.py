#!/usr/bin/env python3
"""
Platium — Advanced OSINT Framework (v4.0)
Author: Neo | Github: pnv21
"""

import sys
import json
import argparse
from modules import username_scanner, email_scanner, phone_scanner, ip_scanner
from modules import exif_extractor, social_analyzer, darknet_scanner, graph_builder
from modules import threat_intel, report_generator
from modules.utils import (
    print_banner, animate_loading, progress_bar, print_header, 
    print_results, cyber_menu, print_status
)

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Platium — Professional OSINT Framework")
    parser.add_argument("-u", "--username", help="Пошук за нікнеймом (60+ платформ)")
    parser.add_argument("-e", "--email", help="Пошук за email (HIBP + утечки)")
    parser.add_argument("-p", "--phone", help="Аналіз номеру телефону")
    parser.add_argument("-i", "--ip", help="Аналіз IP (Shodan + геолокація)")
    parser.add_argument("-f", "--file", help="EXIF-аналіз фото")
    parser.add_argument("-s", "--social", help="Аналіз соцмереж (nick)")
    parser.add_argument("-d", "--darkweb", help="Пошук у даркнеті")
    parser.add_argument("-g", "--graph", help="Побудова графу зв'язків (email)")
    parser.add_argument("-t", "--threat", help="Перевірка загроз (VirusTotal, Shodan)")
    parser.add_argument("-o", "--output", help="Шлях для збереження звіту", default="data/reports/report.txt")
    parser.add_argument("--demo", action="store_true", help="Запустити демонстрацію")
    parser.add_argument("--menu", action="store_true", help="Запустити інтерактивне меню")
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
        sys.exit(0)
    
    if args.menu:
        modules_map = {
            "1": "username", "2": "email", "3": "phone", "4": "ip",
            "5": "file", "6": "social", "7": "darkweb", "8": "graph", "9": "threat"
        }
        choice = cyber_menu(modules_map)
        if choice and choice in modules_map:
            print_status(f"Запуск модуля {modules_map[choice]}...", "info")
        sys.exit(0)
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    
    results = {}
    total_tasks = 0
    completed = 0
    
    # Словник для маппінгу аргументів на модулі
    modules = {
        "username": (args.username, username_scanner.search, "Username Scan"),
        "email": (args.email, email_scanner.search, "Email Check"),
        "phone": (args.phone, phone_scanner.search, "Phone Analysis"),
        "ip": (args.ip, ip_scanner.search, "IP Geolocation"),
        "file": (args.file, exif_extractor.extract, "EXIF Extraction"),
        "social": (args.social, social_analyzer.search, "Social Analysis"),
        "darkweb": (args.darkweb, darknet_scanner.search, "Darknet Scan"),
        "graph": (args.graph, graph_builder.build, "Graph Building"),
        "threat": (args.threat, threat_intel.check, "Threat Intelligence")
    }
    
    for name, (arg_value, func, label) in modules.items():
        if arg_value:
            total_tasks += 1
            print_status(f"Запуск {label}: {arg_value}", "info")
            animate_loading()
            results[name] = func(arg_value)
            completed += 1
            progress_bar(completed, total_tasks, label)
    
    # Вивід результатів
    print_results(results)
    
    # Генерація звіту
    report_generator.generate(results, args.output)
    print_status(f"Звіт збережено у: {args.output}", "success")
    
    # Якщо є email — будуємо граф зв'язків автоматично
    if args.email:
        print_status("Автоматичний аналіз зв'язків...", "info")
        graph_builder.build(args.email)

def run_demo():
    """Демонстрація можливостей Platium"""
    print_header("🚀 ДЕМОНСТРАЦІЯ МОЖЛИВОСТЕЙ PLATIUM")
    
    test_cases = [
        ("USERNAME", "pnv21"),
        ("EMAIL", "test@example.com"),
        ("PHONE", "+380991234567"),
        ("IP", "8.8.8.8"),
    ]
    
    for i, (test_name, test_value) in enumerate(test_cases, 1):
        print_status(f"[{i}/{len(test_cases)}] Аналіз: {test_name} = {test_value}", "info")
        animate_loading()
        time.sleep(1)
        print_status("Успішно", "success")
    
    demo_results = {
        "username": {"GitHub": "https://github.com/pnv21", "found_on": 8},
        "email": {"breaches": ["Adobe", "LinkedIn"], "public_sources": 15}
    }
    print("\n📋 ПРИКЛАД РЕЗУЛЬТАТІВ:")
    print(json.dumps(demo_results, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print_status("Демонстрація завершена.", "success")

if __name__ == "__main__":
    main()
