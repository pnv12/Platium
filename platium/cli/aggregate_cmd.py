import json
import sys

from platium.intelligence.aggregator import (
    store_scan_result,
    generate_analysis_report,
    find_connections,
    aggregate_entity,
)
from platium.intelligence.correlation import run_full_correlation
from platium.scanners.email.scanner import search as email_search
from platium.scanners.username.scanner import search as username_search
from platium.scanners.phone.scanner import search as phone_search
from platium.scanners.ip.scanner import search as ip_search
from platium.ui.display import get_ui


def register(subparsers):
    parser = subparsers.add_parser(
        "aggregate",
        help="Scan and store intelligence data"
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
    ui = get_ui(verbose=getattr(args, "_verbose", False))

    scanners = {
        "email": email_search,
        "username": username_search,
        "phone": phone_search,
        "ip": ip_search,
    }

    scanner = scanners.get(args.type)

    if scanner is None:
        ui.error(f"Unsupported type: {args.type}")
        sys.exit(1)

    try:
        ui.info(
            f"Scanning and storing {args.type}: {args.query}"
        )

        result = scanner(args.query)
        entity_id = store_scan_result(result)

        ui.success(
            f"Data stored for '{args.query}' "
            f"(entity_id: {entity_id})"
        )

    except Exception as exc:
        ui.error(f"Error: {exc}")
        sys.exit(1)


def register_analyze(subparsers):
    parser = subparsers.add_parser(
        "analyze",
        help="Show intelligence database statistics"
    )
    parser.set_defaults(func=run_analyze)


def run_analyze(args):
    ui = get_ui(verbose=getattr(args, "_verbose", False))

    try:
        report = generate_analysis_report()

        if getattr(args, "_quiet", False):
            print(json.dumps(report, ensure_ascii=False))
            return

        ui.info("Intelligence database analysis:")
        print(
            json.dumps(
                report,
                indent=2,
                ensure_ascii=False
            )
        )

    except Exception as exc:
        ui.error(f"Error: {exc}")
        sys.exit(1)


def register_connections(subparsers):
    parser = subparsers.add_parser(
        "connections",
        help="Find outgoing connections for an entity"
    )
    parser.add_argument(
        "query",
        help="Entity value"
    )
    parser.set_defaults(func=run_connections)


def run_connections(args):
    ui = get_ui(verbose=getattr(args, "_verbose", False))

    try:
        connections = find_connections(args.query)

        if not connections:
            ui.info(
                f"No outgoing connections found for '{args.query}'"
            )
            return

        ui.info(
            f"Outgoing connections for '{args.query}':"
        )

        print(
            json.dumps(
                connections,
                indent=2,
                ensure_ascii=False
            )
        )

    except Exception as exc:
        ui.error(f"Error: {exc}")
        sys.exit(1)


def register_entity(subparsers):
    parser = subparsers.add_parser(
        "entity",
        help="Show aggregated intelligence for an entity"
    )
    parser.add_argument(
        "query",
        help="Entity value"
    )
    parser.set_defaults(func=run_entity)


def run_entity(args):
    ui = get_ui(verbose=getattr(args, "_verbose", False))

    try:
        result = aggregate_entity(args.query)

        if result is None:
            ui.error(
                f"Entity not found: '{args.query}'"
            )
            sys.exit(1)

        print(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False
            )
        )

    except Exception as exc:
        ui.error(f"Error: {exc}")
        sys.exit(1)


def register_correlate(subparsers):
    parser = subparsers.add_parser(
        "correlate",
        help="Find and save relationships between entities"
    )
    parser.set_defaults(func=run_correlate)


def run_correlate(args):
    ui = get_ui(verbose=getattr(args, "_verbose", False))

    try:
        ui.info("Running correlation engine...")

        relationships = run_full_correlation()

        if relationships:
            ui.success(
                "Correlation completed: "
                f"{len(relationships)} new relationships found"
            )
        else:
            ui.success(
                "Correlation completed: "
                "no new relationships found"
            )

    except Exception as exc:
        ui.error(f"Error: {exc}")
        sys.exit(1)
