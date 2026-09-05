#!/usr/bin/env python3
import argparse
import sys
from platium.ui.display import display_banner, print_header, print_scan_result, colorize, Color
from platium.cli import (
    username_cmd,
    email_cmd,
    phone_cmd,
    ip_cmd,
    exif_cmd,
    social_cmd,
    threat_cmd,
    graph_cmd,
    darknet_cmd,
    deep_cmd,
    aggregate_cmd,
    report_cmd
)

def main():
    display_banner()
    print_header("PLATIUM PROFESSIONAL CLI", Color.BOLD)

    parser = argparse.ArgumentParser(
        prog="platium",
        description="Advanced OSINT Framework",
        epilog="Use 'platium <command> --help' for more info"
    )
    parser.add_argument("--version", action="version", version="Platium 0.2.0")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--quiet", "-q", action="store_true", help="Quiet mode (only errors)")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- ОСНОВНІ КОМАНДИ ---
    username_cmd.register(subparsers)
    email_cmd.register(subparsers)
    phone_cmd.register(subparsers)
    ip_cmd.register(subparsers)
    exif_cmd.register(subparsers)
    social_cmd.register(subparsers)
    threat_cmd.register(subparsers)
    graph_cmd.register(subparsers)
    darknet_cmd.register(subparsers)
    deep_cmd.register(subparsers)

    # --- КОМАНДИ АГРЕГАТОРА ---
    aggregate_cmd.register(subparsers)
    aggregate_cmd.register_analyze(subparsers)
    aggregate_cmd.register_connections(subparsers)
    aggregate_cmd.register_correlate(subparsers)

    # --- ЗВІТИ ---
    report_cmd.register(subparsers)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        # Передаємо глобальні налаштування в команду
        args._verbose = args.verbose
        args._quiet = args.quiet
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
