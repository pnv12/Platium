import argparse
import sys
import json
from platium.core.errors import ValidationError
from platium.intelligence.aggregator import save_search, find_connections, generate_analysis_report

def register(subparsers):
    parser = subparsers.add_parser("aggregate", help="Save search results to database")
    parser.add_argument("query", help="Query to save")
    parser.add_argument("--type", default="auto", help="Type of query (email, phone, ip, username, etc.)")
    parser.add_argument("--data", help="JSON data to save (must be valid JSON)")
    parser.set_defaults(func=run)

def run(args):
    try:
        # Перевіряємо, чи передано дані
        if not args.data:
            print("[!] Error: --data is required")
            sys.exit(1)
        
        # Валідуємо JSON
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError as e:
            print(f"[!] Invalid JSON: {e}")
            sys.exit(1)

        # Зберігаємо
        save_search(args.query, args.type, data)
        print(f"[+] Data for '{args.query}' saved to database")
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
    parser = subparsers.add_parser("connections", help="Find connections for a query")
    parser.add_argument("query", help="Query to find connections for")
    parser.set_defaults(func=run_connections)

def run_connections(args):
    try:
        conns = find_connections(args.query)
        print(json.dumps(conns, indent=2))
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
