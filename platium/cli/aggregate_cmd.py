import argparse
import sys
import json

from platium.core.normalizer import store_normalized_result
from platium.scanners.email.scanner import search as email_search
from platium.scanners.username.scanner import search as username_search
from platium.scanners.phone.scanner import search as phone_search
from platium.scanners.ip.scanner import search as ip_search
from platium.intelligence.aggregator import (
    find_connections,
    generate_analysis_report
)
from platium.intelligence.correlation import run_full_correlation


def register(subparsers):
    parser = subparsers.add_parser(
        "aggregate",
        help="Store scan results in database"
    )
    parser.add_argument(
        "query",
        help="Target to scan and store"
    )
    parser.add_argument(
        "--type",
        default="email",
        choices=["email", "username", "phone", "ip"],
        help="Target type"
    )
    parser.set_defaults(func=run)


def run(args):
    try:
        scanners = {
            "email": email_search,
            "username": username_search,
            "phone": phone_search,
            "ip": ip_search,
        }

        scanner = scanners.get(args.type)

        if not scanner:
            print(f"[!] Unsupported type: {args.type}")
            sys.exit(1)

        result = scanner(args.query)
        entity_id = store_normalized_result(result)

        print(
            f"[+] Data for '{args.query}' stored "
            f"(entity_id: {entity_id})"
        )

    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


def register_analyze(subparsers):
    parser = subparsers.add_parser(
        "analyze",
        help="Generate analysis report from saved data"
    )
    parser.set_defaults(func=run_analyze)


def run_analyze(args):
    try:
        report = generate_analysis_report()
        print(json.dumps(report, indent=2))

    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


def register_connections(subparsers):
    parser = subparsers.add_parser(
        "connections",
        help="Find connections for an entity"
    )
    parser.add_argument(
        "query",
        help="Entity value to find connections for"
    )
    parser.set_defaults(func=run_connections)


def run_connections(args):
    try:
        conns = find_connections(args.query)
        print(json.dumps(conns, indent=2))

    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)


def register_correlate(subparsers):
    parser = subparsers.add_parser(
        "correlate",
        help="Find and save relationships between entities"
    )
    parser.set_defaults(func=run_correlate)


def run_correlate(args):
    try:
        relationships = run_full_correlation()

        if relationships:
            print(
                f"[+] Correlation completed: "
                f"{len(relationships)} relationships found"
            )
        else:
            print("[+] Correlation completed: no new relationships found")

    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
