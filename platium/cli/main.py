#!/usr/bin/env python3
import argparse
import sys
from platium.ui.display import display_banner
from platium.cli import username_cmd

def main():
    display_banner()
    parser = argparse.ArgumentParser(
        prog="platium",
        description="Advanced OSINT Framework",
        epilog="Use 'platium <command> --help' for more info"
    )
    parser.add_argument("--version", action="version", version="Platium 0.1.0")
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")
    
    # Реєстрація команд
    username_cmd.register(subparsers)
    # email_cmd.register(subparsers)   # додамо пізніше
    # phone_cmd.register(subparsers)
    # ip_cmd.register(subparsers)
    # exif_cmd.register(subparsers)
    # report_cmd.register(subparsers)
    
    args = parser.parse_args()
    
    # Універсальний виклик — args.func(args)
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
