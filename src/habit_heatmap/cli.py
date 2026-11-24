"""Command-line interface for habit-heatmap."""

from __future__ import annotations

import argparse
import sys
from datetime import date, datetime
from pathlib import Path

from .colors import THEMES
from .parser import load_events
from .render_svg import render_svg
from .version import __version__


def iso_date(raw: str) -> date:
    """argparse ``type=`` callable for a YYYY-MM-DD flag value.

    Named without a leading underscore so argparse's error message
    ("invalid iso_date value: ...") reads cleanly instead of exposing
    a private helper's name.
    """
    return datetime.strptime(raw, "%Y-%m-%d").date()


def parse_steps(raw: str) -> float | tuple[float, ...]:
    """Parse one step width or four comma-separated step widths."""
    try:
        if "," not in raw:
            return float(raw)
        values = tuple(float(value.strip()) for value in raw.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "steps must be a number or four comma-separated numbers"
        ) from exc

    if len(values) != 4:
        raise argparse.ArgumentTypeError(
            "steps must be a number or four comma-separated numbers"
        )
    return values


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="habit-heatmap",
        description="Generate a GitHub-style contribution heatmap from a CSV of dated events.",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument("csv", help="path to the input CSV file, or - to read from stdin")
    parser.add_argument(
        "-o", "--output", required=True, help="output file path (.svg or .png), or - for stdout"
    )
    parser.add_argument("--date-col", default="date", help="date column name (default: date)")
    parser.add_argument(
        "--value-col", default=None, help="numeric column to sum per day (default: count rows)"
    )
    parser.add_argument("--date-format", default=None, help="explicit strptime format for dates")
    parser.add_argument(
        "--tz",
        default=None,
        help="IANA zone (e.g. America/Chicago) to normalize timestamps to before bucketing",
    )
    parser.add_argument(
        "--start", type=iso_date, default=None, help="first day to render (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--end", type=iso_date, default=None, help="last day to render (YYYY-MM-DD)"
    )
    parser.add_argument(
        "--theme",
        default="github",
        choices=sorted(THEMES),
        help="color theme (default: github)",
    )
    parser.add_argument(
        "--steps",
        type=parse_steps,
        default=None,
        help=(
            "intensity step widths: one positive number (repeated four times), "
            "or four comma-separated positive widths"
        ),
    )
    parser.add_argument("--label", default=None, help="title rendered above the chart")
    parser.add_argument(
        "--month-label-font-size",
        type=float,
        default=9,
        help="font size for month labels in SVG units (default: 9)",
    )
    parser.add_argument(
        "--month-label-color",
        default="#767676",
        help="hex color for month labels (default: #767676)",
    )
    parser.add_argument(
        "--weekday-label-font-size",
        type=float,
        default=9,
        help="font size for weekday labels in SVG units (default: 9)",
    )
    parser.add_argument(
        "--weekday-label-color",
        default="#767676",
        help="hex color for weekday labels (default: #767676)",
    )
    parser.add_argument(
        "--week-start",
        default="sunday",
        choices=("sunday", "monday"),
        help="first weekday of each grid column (default: sunday)",
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--verbose", action="store_true", help='print the "wrote <path>" message (default: off)'
    )
    verbosity.add_argument(
        "--quiet", action="store_true", help="suppress all output (the default; kept for clarity)"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        counts = load_events(
            args.csv,
            date_col=args.date_col,
            value_col=args.value_col,
            date_format=args.date_format,
            tz=args.tz,
        )
        svg = render_svg(
            counts,
            start=args.start,
            end=args.end,
            theme=args.theme,
            label=args.label,
            week_start=args.week_start,
            steps=args.steps,
            month_label_font_size=args.month_label_font_size,
            month_label_color=args.month_label_color,
            weekday_label_font_size=args.weekday_label_font_size,
            weekday_label_color=args.weekday_label_color,
        )

        if args.output == "-":
            sys.stdout.write(svg)
        else:
            output = Path(args.output)
            if output.suffix.lower() == ".png":
                from .render_png import svg_to_png

                svg_to_png(svg, str(output))
            else:
                output.write_text(svg, encoding="utf-8")
    except (ValueError, OSError, RuntimeError, LookupError) as exc:
        print(f"habit-heatmap: error: {exc}", file=sys.stderr)
        return 1

    if args.verbose:
        print(f"wrote {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
