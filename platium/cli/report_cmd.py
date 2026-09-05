import argparse
import sys
from platium.reports.generator import generate_report

def register(subparsers):
    parser = subparsers.add_parser("report", help="Generate report for a target")
    parser.add_argument("query", help="Target entity value")
    parser.add_argument("--format", "-f", default="html", choices=["html", "json", "md", "pdf"], help="Output format")
    parser.set_defaults(func=run)

def run(args):
    try:
        output_path = generate_report(args.query, args.format)
        print(f"[+] Report saved to: {output_path}")
    except ValueError as e:
        print(f"[!] Error: {e}")
        sys.exit(1)
    except NotImplementedError as e:
        print(f"[!] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        sys.exit(1)
