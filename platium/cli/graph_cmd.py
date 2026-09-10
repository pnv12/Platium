import json
import sys

from platium.core.validators import validate_email, validate_username
from platium.core.errors import ValidationError, ScannerError
from platium.core.config import load_config
from platium.ui.display import get_ui
from platium.scanners.graph.scanner import search


def register(subparsers):
    parser = subparsers.add_parser(
        "graph",
        help="Build connection graph"
    )

    parser.add_argument(
        "query",
        help="Email or username for graph"
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Save report to file"
    )

    parser.set_defaults(func=run)


def run(args):
    ui = get_ui(
        verbose=getattr(args, "_verbose", False)
    )

    try:
        try:
            validate_email(args.query)
            target_type = "email"
        except ValidationError:
            validate_username(args.query)
            target_type = "username"

        ui.info(
            f"Building graph for {target_type}: {args.query}"
        )

        config = load_config()

        results = search(
            args.query,
            config,
            getattr(args, "verbose", False)
            or getattr(args, "_verbose", False)
        )

        if args.json:
            print(
                json.dumps(
                    results,
                    indent=2,
                    ensure_ascii=False
                )
            )
        else:
            ui.print_result(
                results,
                "graph"
            )

        if args.output:
            with open(
                args.output,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    results,
                    file,
                    indent=2,
                    ensure_ascii=False
                )

            ui.success(
                f"Report saved to {args.output}"
            )

    except ValidationError as exc:
        ui.error(
            f"Invalid input: {exc}"
        )
        sys.exit(1)

    except ScannerError as exc:
        ui.error(
            f"Scanner error: {exc}"
        )
        sys.exit(1)

    except Exception as exc:
        ui.error(
            f"Unexpected error: {exc}"
        )
        sys.exit(1)
