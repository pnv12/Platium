#!/usr/bin/env python3
import argparse
import sys
from platium.ui.display import display_banner
from platium.cli import username_cmd

def main():
    display_banner()
    parser = argparse.ArgumentParser(prog="platium", description="Advanced OSINT Framework")
    subparsers = parser.add_subparsers(dest="command", required=True)

    username_cmd.register(subparsers)

    args = parser.parse_args()
    if args.command == "username":
        username_cmd.run(args)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
