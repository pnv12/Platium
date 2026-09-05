import argparse
import sys
import json
from platium.core.validators import validate_ip
from platium.core.errors import ValidationError
from platium.core.config import load_config
from platium.scanners.ip.scanner import search

def register(subparsers):
    parser = subparsers.add_parser("ip", help="Analyze IP address")
    parser.add_argument("query", help="IP address to analyze")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-o", "--output", help="Save report to file")
    parser.set_defaults(func=run)

def run(args):
    try:
        validate_ip(args.query)
        config = load_config()
        result = search(args.query, config, args.verbose)

        if args.json:
            print(result.to_json())
        else:
            print(f"\n[+] Results for IP:")
            print(result.to_json())

        if args.output:
            with open(args.output, 'w') as f:
                f.write(result.to_json())
            print(f"[+] Report saved to {args.output}")

    except ValidationError as e:
        print(f"[!] Invalid IP: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)
