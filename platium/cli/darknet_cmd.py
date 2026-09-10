import sys

from platium.core.validators import validate_username
from platium.core.errors import ValidationError, ScannerError
from platium.core.config import load_config
from platium.ui.display import get_ui
from platium.scanners.darknet.scanner import search


def register(subparsers):
    parser = subparsers.add_parser(
        "darknet",
        help="Search in darknet (Ahmia)"
    )

    parser.add_argument(
        "query",
        help="Search query"
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
        validate_username(args.query)

        ui.info(
            f"Searching darknet: {args.query}"
        )

        config = load_config()

        result = search(
            args.query,
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
                "darknet"
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
            f"Invalid username: {exc}"
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
