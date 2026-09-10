import sys

from platium.core.config import load_config
from platium.core.errors import ValidationError, ScannerError
from platium.ui.display import get_ui
from platium.scanners.deep.scanner import deep_search


def register(subparsers):
    parser = subparsers.add_parser(
        "deep",
        help="Deep OSINT search (auto-detect type)"
    )

    parser.add_argument(
        "query",
        help="Email, phone, IP, or username"
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
        ui.info(
            f"Starting deep search: {args.query}"
        )

        config = load_config()

        result = deep_search(
            args.query,
            config,
            getattr(args, "verbose", False)
            or getattr(args, "_verbose", False)
        )

        if args.json:
            print(
                result.to_json()
            )
        else:
            ui.print_result(
                result.to_dict(),
                "deep"
            )

        if args.output:
            with open(
                args.output,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(
                    result.to_json()
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
