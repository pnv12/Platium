import sys

from platium.reports.generator import generate_report
from platium.ui.display import get_ui


def register(subparsers):
    parser = subparsers.add_parser(
        "report",
        help="Generate report for a target"
    )

    parser.add_argument(
        "query",
        help="Target entity value"
    )

    parser.add_argument(
        "--format",
        "-f",
        default="html",
        choices=["html", "json", "md", "pdf"],
        help="Output format"
    )

    parser.set_defaults(func=run)


def run(args):
    ui = get_ui(
        verbose=getattr(args, "_verbose", False)
    )

    try:
        ui.info(
            f"Generating {args.format.upper()} report: {args.query}"
        )

        output_path = generate_report(
            args.query,
            args.format
        )

        ui.success(
            f"Report saved to: {output_path}"
        )

    except ValueError as exc:
        ui.error(
            f"Error: {exc}"
        )
        sys.exit(1)

    except NotImplementedError as exc:
        ui.error(
            str(exc)
        )
        sys.exit(1)

    except Exception as exc:
        ui.error(
            f"Unexpected error: {exc}"
        )
        sys.exit(1)
