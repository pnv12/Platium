import argparse
import sys
import json
from platium.core.validators import validate_phone
from platium.core.errors import ValidationError, ScannerError
from platium.core.config import load_config
from platium.ui.display import print_result
from platium.scanners.phone.scanner import search

def register(subparsers):
    parser = subparsers.add_parser("phone", help="Analyze phone number")
    parser.add_argument("query", help="Phone number to analyze")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-o", "--output", help="Save report to file")
    parser.set_defaults(func=run)

def run(args):
    try:
        validate_phone(args.query)
        config = load_config()
        results = search(args.query, config, args.verbose)
        
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print_result(results, "phone")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"[+] Report saved to {args.output}")
            
    except ValidationError as e:
        print(f"[!] Invalid phone number: {e}")
        sys.exit(1)
    except ScannerError as e:
        print(f"[!] Scanner error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)
