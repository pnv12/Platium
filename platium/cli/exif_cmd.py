import argparse
import sys
import json
from platium.core.config import config
from platium.scanners.exif.scanner import search

def register(subparsers):
    parser = subparsers.add_parser("exif", help="Extract EXIF metadata from image")
    parser.add_argument("query", help="Path to image file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("-o", "--output", help="Save report to file")
    parser.set_defaults(func=run)

def run(args):
    try:
        result = search(args.query, args.verbose)
        if args.json:
            print(result.to_json())
        else:
            print(f"\n[+] Results for EXIF:")
            print(result.to_json())
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result.to_json())
            print(f"[+] Report saved to {args.output}")
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
