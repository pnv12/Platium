import argparse
import sys
from platium.core.validators import validate_username
from platium.core.errors import ValidationError, ScannerError
from platium.core.config import load_config
from platium.ui.display import print_result
from modules.username_scanner import search

def register(subparsers):
    parser = subparsers.add_parser("username", help="Search by username")
    parser.add_argument("query", help="Username to search")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose")
    parser.set_defaults(func=run)

def run(args):
    try:
        validate_username(args.query)
        config = load_config()
        results = search(args.query, config, args.verbose)
        print_result(results, "username")
    except ValidationError as e:
        print(f"[!] Invalid input: {e}")
        sys.exit(1)
    except ScannerError as e:
        print(f"[!] Scanner error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)
