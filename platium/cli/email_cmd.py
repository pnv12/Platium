import sys

from platium.core.validators import validate_email
from platium.core.errors import ValidationError
from platium.core.config import load_config
from platium.scanners.email.scanner import search
from platium.ui.display import get_ui


def register(subparsers):
    parser = subparsers.add_parser(
        "email",
        help="Check email for data breaches"
    )

    parser.add_argument(
        "query",
        help="Email address to check"
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
        validate_email(args.query)

        ui.info(
            f"Scanning email: {args.query}"
        )

        config = load_config()

        result = search(
            args.query,
            config,
            getattr(args, "verbose", False)
            or getattr(args, "_verbose", False)
        )

        if args.json:
            print(result.to_json())
        else:
            ui.print_result(
                result.to_dict(),
                scan_type="email"
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
            f"Invalid email: {exc}"
        )
        sys.exit(1)

    except Exception as exc:
        ui.error(
            f"Unexpected error: {exc}"
        )
        sys.exit(1)
