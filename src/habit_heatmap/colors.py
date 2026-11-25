"""Color scales for mapping event intensity to heatmap cell colors."""

from __future__ import annotations

from collections.abc import Sequence
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
    steps: Sequence[float] | None = None,
) -> tuple[float, float, float]:
    """Return the three color-change thresholds for a five-color scale.

    If steps is None, preserve Quilt's original behavior by placing the
    thresholds at one quarter, one half, and three quarters of the observed
    maximum. Otherwise, steps must contain exactly three positive, finite,
    strictly increasing threshold values. The supplied values are used
    directly; they are never treated as interval widths or accumulated.

    The lightest palette color is reserved for zero and negative values.
    The three thresholds separate the four colors used for positive values.
    Values at or above the third threshold use the darkest color.
    """
    if steps is None:
        width = max_value / 4 if max_value > 0 else 0.0
        return (width, 2 * width, 3 * width)

    if isinstance(steps, (str, bytes)) or not isinstance(steps, Sequence):
        raise ValueError(
            "steps must be a sequence of exactly three positive, "
            "strictly increasing numeric thresholds"
        )
    if len(steps) != 3:
        raise ValueError("steps must contain exactly three thresholds")

    if any(isinstance(value, bool) or not isinstance(value, Real) for value in steps):
        raise ValueError("all step thresholds must be numeric")

    thresholds = tuple(float(value) for value in steps)
    if not all(isfinite(value) and value > 0 for value in thresholds):
        raise ValueError("all step thresholds must be positive and finite")
    if not (thresholds[0] < thresholds[1] < thresholds[2]):
        raise ValueError("step thresholds must be strictly increasing")

    return thresholds


def color_for_steps(
    value: float,
    thresholds: Sequence[float],
    palette: tuple[str, ...],
) -> str:
    """Map value to a palette color using exact threshold values.

    Zero and negative values use the no-activity color. A positive value
    moves to the next color when it is greater than or equal to a threshold.
    """
    if value <= 0:
        return palette[0]

    index = 1 + sum(value >= threshold for threshold in thresholds)
    return palette[min(index, len(palette) - 1)]


def bucket_color(
    value: float,
    max_value: float,
    palette: tuple[str, ...],
    steps: Sequence[float] | None = None,
) -> str:
    """Map value to a palette color.

    The three-argument call retains the original automatic scaling.
    The optional steps argument supplies the three exact color-change thresholds.
    """
    if value <= 0 or (steps is None and max_value <= 0):
        return palette[0]
    return color_for_steps(value, resolve_steps(max_value, steps), palette)
