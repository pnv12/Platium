#!/usr/bin/env python3
"""
Platium — Advanced OSINT Framework (v4.0)
Author: Neo | Github: pnv21
"""

import sys
import json
import time
import argparse
from datetime import datetime
from modules import username_scanner, email_scanner, phone_scanner, ip_scanner
from modules import exif_extractor, social_analyzer, darknet_scanner, graph_builder
from modules import threat_intel, report_generator
from modules.ui import display_banner, animate_loading, progress_bar, print_header, cyber_menu

def main():
    display_banner()
    
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
        cyber_menu()
        sys.exit(0)
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    
    results = {}
    total_tasks = 0
    completed = 0
    
    if args.username:
        total_tasks += 1
        print(f"\n🔍 [1/{total_tasks}] Пошук за нікнеймом: {args.username}")
        animate_loading()
        results["username"] = username_scanner.search(args.username)
        completed += 1
        progress_bar(completed, total_tasks, "Username Scan")
    
    if args.email:
        total_tasks += 1
        print(f"\n📧 [2/{total_tasks}] Пошук за email: {args.email}")
        animate_loading()
        results["email"] = email_scanner.search(args.email)
        completed += 1
        progress_bar(completed, total_tasks, "Email Check")
    
    if args.phone:
        total_tasks += 1
        print(f"\n📱 [3/{total_tasks}] Аналіз номеру: {args.phone}")
        animate_loading()
        results["phone"] = phone_scanner.search(args.phone)
        completed += 1
        progress_bar(completed, total_tasks, "Phone Analysis")
    
    if args.ip:
        total_tasks += 1
        print(f"\n🌍 [4/{total_tasks}] Аналіз IP: {args.ip}")
        animate_loading()
        results["ip"] = ip_scanner.search(args.ip)
        completed += 1
        progress_bar(completed, total_tasks, "IP Geolocation")
    
    if args.file:
        total_tasks += 1
        print(f"\n🖼️ [5/{total_tasks}] EXIF-аналіз: {args.file}")
        animate_loading()
        results["exif"] = exif_extractor.extract(args.file)
        completed += 1
        progress_bar(completed, total_tasks, "EXIF Extraction")
    
    if args.social:
        total_tasks += 1
        print(f"\n📊 [6/{total_tasks}] Аналіз соцмереж: {args.social}")
        animate_loading()
        results["social"] = social_analyzer.search(args.social)
        completed += 1
        progress_bar(completed, total_tasks, "Social Analysis")
    
    if args.darkweb:
        total_tasks += 1
        print(f"\n🌐 [7/{total_tasks}] Пошук у даркнеті: {args.darkweb}")
        animate_loading()
        results["darknet"] = darknet_scanner.search(args.darkweb)
        completed += 1
        progress_bar(completed, total_tasks, "Darknet Scan")
    
    if args.graph:
        total_tasks += 1
        print(f"\n🔗 [8/{total_tasks}] Побудова графу зв'язків для: {args.graph}")
        animate_loading()
        results["graph"] = graph_builder.build(args.graph)
        completed += 1
        progress_bar(completed, total_tasks, "Graph Building")
    
    if args.threat:
        total_tasks += 1
        print(f"\n🛡️ [9/{total_tasks}] Перевірка загроз: {args.threat}")
        animate_loading()
        results["threat"] = threat_intel.check(args.threat)
        completed += 1
        progress_bar(completed, total_tasks, "Threat Intelligence")
    
    # Вивід результатів
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТИ:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Генерація звіту
    report_generator.generate(results, args.output)
    print(f"\n✅ Звіт збережено у: {args.output}")
    
    # Аналіз зв'язків (якщо є email)
    if args.email:
        print("\n🔗 Автоматичний аналіз зв'язків...")
        graph_builder.build(args.email)

def run_demo():
    """Демонстрація можливостей Platium"""
    print_header("🚀 ДЕМОНСТРАЦІЯ МОЖЛИВОСТЕЙ PLATIUM")
    
    test_cases = [
        ("USERNAME", "pnv21"),
        ("EMAIL", "test@example.com"),
        ("PHONE", "+380991234567"),
        ("IP", "8.8.8.8"),
        ("THREAT", "test@example.com"),
    ]
    
    for i, (test_name, test_value) in enumerate(test_cases, 1):
        print(f"\n🔍 [{i}/{len(test_cases)}] Аналіз: {test_name} = {test_value}")
        animate_loading()
        time.sleep(1)
        print(f"   ✅ Дані успішно зібрано")
    
    print("\n\n📋 ПРИКЛАД РЕЗУЛЬТАТІВ:")
    demo_results = {
        "username": {
            "GitHub": "https://github.com/pnv21",
            "Twitter": "https://twitter.com/pnv21",
            "Instagram": "https://instagram.com/pnv21",
            "found_on": 8
        },
        "email": {
            "breaches": ["Adobe", "LinkedIn", "MySpace"],
            "public_sources": 15
        },
        "graph": {
            "connections": ["pnv21", "neo", "saturn"],
            "links": 3
        }
    }
    print(json.dumps(demo_results, indent=2, ensure_ascii=False))
    
    print("\n" + "="*60)
    print("✅ Демонстрація завершена. Використовуйте --help для отримання довідки.")

if __name__ == "__main__":
    main()
