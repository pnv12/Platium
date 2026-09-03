import argparse
import sys
import json
from platium.core.errors import ScannerError
from platium.intelligence.aggregator import save_search, find_connections, generate_analysis_report

def register(subparsers):
    parser = subparsers.add_parser("aggregate", help="Save search results to database")
    parser.add_argument("query", help="Query to save")
    parser.add_argument("--type", default="auto", help="Type of query (email, phone, ip, username)")
    parser.add_argument("--data", help="JSON data to save (optional)")
    parser.set_defaults(func=run)

def run(args):
    try:
        # Якщо дані не надані — шукаємо (але тут просто заглушка)
        data = {"status": "saved", "message": "Data saved manually"}
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
