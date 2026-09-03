import argparse
import sys
import json
from platium.core.errors import ScannerError
from platium.reports.generator import generate_report

def register(subparsers):
    parser = subparsers.add_parser("report", help="Generate report from data")
    parser.add_argument("--data", help="JSON data or file path with data")
    parser.add_argument("--file", help="Path to JSON file with data")
    parser.add_argument("-o", "--output", required=True, help="Output path (without extension)")
    parser.add_argument("-f", "--format", default="txt", choices=["txt", "json", "html"], help="Report format")
    parser.set_defaults(func=run)

def run(args):
    try:
        data = None
        if args.file:
            with open(args.file, 'r') as f:
                data = json.load(f)
        elif args.data:
            data = json.loads(args.data)
        else:
            print("[!] Please provide data via --data or --file")
            sys.exit(1)
        
        result_path = generate_report(data, args.output, args.format)
        print(f"[+] Report saved to {result_path}")
        
    except Exception as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
