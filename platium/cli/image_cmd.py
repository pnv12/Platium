import sys

from platium.ui.display import get_ui
from platium.scanners.image.scanner import search


def register(subparsers):
    parser = subparsers.add_parser(
        "image",
        help="Analyze image and calculate fingerprints"
    )

    parser.add_argument(
        "query",
        help="Path to image file"
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
        help="Save result to file"
    )

    parser.set_defaults(func=run)


def run(args):
    ui = get_ui(
        verbose=getattr(args, "_verbose", False)
    )

    try:
        ui.info(
            f"Analyzing image: {args.query}"
        )

        result = search(
            args.query,
            getattr(args, "verbose", False)
            or getattr(args, "_verbose", False)
        )

        if args.json:
            print(result.to_json())
        else:
            ui.print_result(
                result.to_dict(),
                "image"
            )

        if args.output:
            with open(
                args.output,
                "w",
                encoding="utf-8"
            ) as file:
                file.write(result.to_json())

            ui.success(
                f"Report saved to {args.output}"
            )

    except Exception as exc:
        ui.error(
            f"Error: {exc}"
        )
        sys.exit(1)
