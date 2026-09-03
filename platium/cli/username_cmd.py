import argparse
import sys
from platium.core.validators import validate_username
from platium.core.errors import ValidationError, ScannerError
from platium.core.config import load_config
from platium.ui.display import print_result
from platium.scanners.username.scanner import search  # НОВИЙ ІМПОРТ

def register(subparsers):
    parser = subparsers.add_parser("username", help="Search by username")
    parser.add_argument("query", help="Username to search")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-o", "--output", help="Save report to file")
    parser.set_defaults(func=run)

def run(args):
    try:
        validate_username(args.query)
        config = load_config()
        results = search(args.query, config, args.verbose)
        
        if args.json:
            import json
            print(json.dumps(results, indent=2))
        else:
            print_result(results, "username")
        
        if args.output:
            with open(args.output, 'w') as f:
                import json
                json.dump(results, f, indent=2)
            print(f"[+] Report saved to {args.output}")
            
    except ValidationError as e:
        print(f"[!] Invalid input: {e}")
        sys.exit(1)
    except ScannerError as e:
        print(f"[!] Scanner error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)
