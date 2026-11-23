"""Color scales for mapping event intensity to heatmap cell colors."""

from __future__ import annotations

from collections.abc import Sequence
from itertools import accumulate
from math import isfinite
from numbers import Real

# GitHub's classic green scale, lightest (no activity) to darkest.
GITHUB_GREEN = ("#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39")

THEMES: dict[str, tuple[str, ...]] = {
    "github": GITHUB_GREEN,
    "blue": ("#ebedf0", "#c6dbef", "#6baed6", "#3182bd", "#08519c"),
    "purple": ("#ebedf0", "#dadaeb", "#9e9ac8", "#6a51a3", "#3f007d"),
    "mono": ("#ebedf0", "#c4c4c4", "#8c8c8c", "#545454", "#1a1a1a"),
    "dark": ("#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"),
}


def resolve_steps(
    max_value: float,
    steps: float | Sequence[float] | None = None,
) -> tuple[float, float, float, float]:
    """Return the cumulative limits for a five-color intensity scale.

    ``steps=None`` preserves Quilt's original behaviour by dividing the
    observed maximum into four equal-width steps. A positive scalar is
    repeated four times. A sequence must contain exactly four positive
    step widths; its cumulative sums define the scale limits.

    The first three cumulative limits separate the four non-zero colors.
    The fourth is the nominal upper end of the darkest color's interval;
    values above it remain in the darkest color.
    """
    if steps is None:
        width = max_value / 4 if max_value > 0 else 0.0
        widths = (width, width, width, width)
    elif isinstance(steps, bool):
        raise ValueError("steps must be a positive number or a sequence of four positive numbers")
    elif isinstance(steps, Real):
        width = float(steps)
        if not isfinite(width) or width <= 0:
            raise ValueError("steps must be a positive finite number")
        widths = (width, width, width, width)
    else:
        if isinstance(steps, (str, bytes)) or not isinstance(steps, Sequence):
            raise ValueError(
                "steps must be None, a positive number, or a sequence of four positive numbers"
            )
        if len(steps) != 4:
            raise ValueError("steps sequence must contain exactly four values")
        try:
            widths = tuple(float(value) for value in steps)
        except (TypeError, ValueError) as exc:
            raise ValueError("all step widths must be numeric") from exc
        if not all(isfinite(width) and width > 0 for width in widths):
            raise ValueError("all step widths must be positive and finite")

    return tuple(accumulate(widths))


def color_for_steps(
    value: float,
    cumulative_steps: Sequence[float],
    palette: tuple[str, ...],
) -> str:
    """Map ``value`` to a palette color using resolved cumulative limits.

    Zero and negative values use the no-activity color. Positive values
    move to the next color when they reach one of the first three limits.
    """
    if value <= 0:
        return palette[0]

    # Five colors include a dedicated zero-activity color, leaving four
    # colors for positive activity and therefore three color transitions.
    index = 1 + sum(value >= threshold for threshold in cumulative_steps[:3])
    return palette[min(index, len(palette) - 1)]


def bucket_color(
    value: float,
    max_value: float,
    palette: tuple[str, ...],
    steps: float | Sequence[float] | None = None,
) -> str:
    """Map ``value`` to a palette color.

    The three-argument call retains the original automatic scaling. The
    optional ``steps`` argument accepts the same values as ``resolve_steps``.
    """
    if value <= 0 or (steps is None and max_value <= 0):
        return palette[0]
    return color_for_steps(value, resolve_steps(max_value, steps), palette)
