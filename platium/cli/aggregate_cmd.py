import argparse
import sys
import json
from platium.core.errors import ValidationError
from platium.intelligence.aggregator import store_scan_result, find_connections, generate_analysis_report
from platium.scanners.email.scanner import search as email_search
from platium.core.config import load_config

def register(subparsers):
    parser = subparsers.add_parser("aggregate", help="Store scan results in database")
    parser.add_argument("query", help="Target to scan and store")
    parser.add_argument("--type", default="email", choices=["email", "username", "phone", "ip"], help="Target type")
    parser.set_defaults(func=run)

def run(args):
    try:
        config = load_config()
        # Вибираємо сканер за типом
        scanners = {
            "email": email_search,
            # додати інші сканери пізніше
        }
        scanner = scanners.get(args.type)
        if not scanner:
            print(f"[!] Unsupported type: {args.type}")
            sys.exit(1)

        result = scanner(args.query, config)
        store_scan_result(result)
        print(f"[+] Data for '{args.query}' stored in database")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

def register_analyze(subparsers):
    parser = subparsers.add_parser("analyze", help="Generate analysis report from saved data")
    parser.set_defaults(func=run_analyze)

def run_analyze(args):
    try:
        report = generate_analysis_report()
        print(json.dumps(report, indent=2))
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)

def register_connections(subparsers):
    parser = subparsers.add_parser("connections", help="Find connections for an entity")
    parser.add_argument("query", help="Entity value to find connections for")
    parser.set_defaults(func=run_connections)

def run_connections(args):
    try:
        conns = find_connections(args.query)
        print(json.dumps(conns, indent=2))
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
