#!/usr/bin/env python3
"""
Platium — Advanced OSINT Framework (v5.0)
Author: Neo | Github: pnv21
"""

import sys
import json
import time
import argparse
import asyncio
from datetime import datetime
from modules import (
    username_scanner, email_scanner, phone_scanner, ip_scanner,
    exif_extractor, social_analyzer, darknet_scanner, graph_builder,
    threat_intel, report_generator, ui, utils
)

async def run_tasks(args):
    """Запускає всі модулі асинхронно"""
    results = {}
    tasks = []

    if args.username:
        tasks.append(username_scanner.search(args.username))
    if args.email:
        tasks.append(email_scanner.search(args.email))
    if args.phone:
        tasks.append(phone_scanner.search(args.phone))
    if args.ip:
        tasks.append(ip_scanner.search(args.ip))
    if args.file:
        tasks.append(exif_extractor.extract(args.file))
    if args.social:
        tasks.append(social_analyzer.search(args.social))
    if args.darkweb:
        tasks.append(darknet_scanner.search(args.darkweb))
    if args.graph:
        tasks.append(graph_builder.build(args.graph))
    if args.threat:
        tasks.append(threat_intel.check(args.threat))

    if not tasks:
        return {}

    # Виконання всіх задач паралельно
    results_list = await asyncio.gather(*tasks)
    keys = [k for k, v in vars(args).items() if v and k not in ['output', 'demo', 'menu', 'func']]
    for key, res in zip(keys, results_list):
        results[key] = res

    return results

def main():
    ui.display_banner()
    
    parser = argparse.ArgumentParser(description="Platium — Professional OSINT Framework v5.0")
    parser.add_argument("-u", "--username", help="Пошук за нікнеймом (350+ платформ)")
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
    parser.add_argument("--web", action="store_true", help="Запустити веб-сервер для перегляду звітів")
    
    args = parser.parse_args()
    
    if args.demo:
        ui.run_demo()
        sys.exit(0)
    
    if args.menu:
        ui.cyber_menu()
        sys.exit(0)
    
    if args.web:
        utils.start_web_server()
        sys.exit(0)
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    
    ui.print_header("🚀 ЗАПУСК АНАЛІЗУ")
    
    # Асинхронний запуск
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(run_tasks(args))
    
    if not results:
        ui.print_status("Немає даних для аналізу", "error")
        sys.exit(1)
    
    # Вивід результатів
    print("\n" + "="*60)
    print("📊 РЕЗУЛЬТАТИ:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Генерація звіту
    report_generator.generate(results, args.output)
    ui.print_status(f"Звіт збережено у: {args.output}", "success")
    
    # Якщо є email, будуємо граф зв'язків
    if args.email:
        ui.print_status("🔗 Автоматичний аналіз зв'язків...", "info")
        graph_result = loop.run_until_complete(graph_builder.build(args.email))
        print(json.dumps(graph_result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
