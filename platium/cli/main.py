#!/usr/bin/env python3
"""
Platium — Advanced OSINT Framework
CLI entry point
"""

import argparse
import sys
import json
from platium.ui.display import display_banner
from platium.cli import username, email, phone, ip, exif, report
from platium.core import __version__

def main():
    display_banner()
    
    parser = argparse.ArgumentParser(
        prog="platium",
        description="Advanced OSINT Framework for Linux/Termux"
    )
    parser.add_argument("--version", action="version", version=f"Platium {__version__}")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    parser.add_argument("--output", "-o", help="Save results to file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode (no banners)")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Subcommands")

    # Реєстрація команд
    username.register(subparsers)
    email.register(subparsers)
    phone.register(subparsers)
    ip.register(subparsers)
    exif.register(subparsers)
    report.register(subparsers)

    args = parser.parse_args()

    # Якщо команда не вказана, вивести help
    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Запуск відповідної команди
    try:
        result = args.func(args)  # Кожна команда повертає результат
        output_result(result, args)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)

def output_result(result, args):
    """Уніфікований вивід результатів"""
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_result(result)  # Тут буде виклик функції для красивого виводу

if __name__ == "__main__":
    main()
