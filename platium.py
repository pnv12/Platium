#!/usr/bin/env python3
"""
Platium — Advanced OSINT Framework
Author: Neo
Version: 1.0
"""

import sys
import json
import argparse
from datetime import datetime
from modules import username_scanner, email_scanner, phone_scanner, ip_scanner
from modules import exif_extractor, social_analyzer, darknet_scanner, report_generator
from modules.utils import print_banner, validate_input

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(description="Platium — OSINT Framework")
    parser.add_argument("-u", "--username", help="Пошук за нікнеймом")
    parser.add_argument("-e", "--email", help="Пошук за email")
    parser.add_argument("-p", "--phone", help="Аналіз номеру телефону")
    parser.add_argument("-i", "--ip", help="Аналіз IP-адреси")
    parser.add_argument("-f", "--file", help="EXIF-аналіз фото")
    parser.add_argument("-s", "--social", help="Аналіз соцмереж (nick)")
    parser.add_argument("-d", "--darkweb", help="Пошук у даркнеті")
    parser.add_argument("-o", "--output", help="Шлях для збереження звіту", default="data/reports/report.txt")
    
    args = parser.parse_args()
    
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    
    results = {}
    
    if args.username:
        results["username"] = username_scanner.search(args.username)
    
    if args.email:
        results["email"] = email_scanner.search(args.email)
    
    if args.phone:
        results["phone"] = phone_scanner.search(args.phone)
    
    if args.ip:
        results["ip"] = ip_scanner.search(args.ip)
    
    if args.file:
        results["exif"] = exif_extractor.extract(args.file)
    
    if args.social:
        results["social"] = social_analyzer.search(args.social)
    
    if args.darkweb:
        results["darknet"] = darknet_scanner.search(args.darkweb)
    
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТИ:")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    
    # Генерація звіту
    report_generator.generate(results, args.output)
    print(f"\n✅ Звіт збережено у: {args.output}")

if __name__ == "__main__":
    main()
