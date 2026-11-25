"""Color scales for mapping event intensity to heatmap cell colors."""

from __future__ import annotations

from bisect import bisect_right
from collections.abc import Sequence
from math import isfinite
from numbers import Real

# GitHub classic green scale, lightest to darkest.
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
) -> tuple[float, float, float, float, float]:
    """Resolve five ordered intensity levels, one for each palette color.

    When omitted, return the five reference levels for the automatic scale.
    When supplied, ``steps`` must contain exactly five finite, strictly
    increasing numeric values. Each value is the lower level associated with
    its corresponding palette color. Values below the first level use the
    first color; reaching each subsequent level changes to its color.

    The five entries are levels, not interval widths. They are never added
    together or interpreted cumulatively.
    """
    if steps is None:
        width = max_value / 4 if max_value > 0 else 0.0
        return (0.0, width, 2 * width, 3 * width, max_value)

    if isinstance(steps, (str, bytes)) or not isinstance(steps, Sequence):
        raise ValueError(
            "steps must be a sequence of exactly five finite, "
            "strictly increasing numeric levels"
        )
    if len(steps) != 5:
        raise ValueError("steps must contain exactly five intensity levels")

    if any(isinstance(value, bool) or not isinstance(value, Real) for value in steps):
        raise ValueError("all step levels must be numeric")

    levels = tuple(float(value) for value in steps)
    if not all(isfinite(value) for value in levels):
        raise ValueError("all step levels must be finite")
    if not all(left < right for left, right in zip(levels, levels[1:])):
        raise ValueError("step levels must be strictly increasing")

    return levels


def color_for_steps(
    value: float,
    levels: Sequence[float],
    palette: tuple[str, ...],
) -> str:
    """Map ``value`` to the color for the greatest configured level it reaches.

    Each level corresponds to the palette entry at the same index. Values
    below the first level are clamped to the first color, and values at or
    above the last level use the darkest color.
    """
    index = max(0, bisect_right(levels, value) - 1)
    return palette[min(index, len(palette) - 1)]


def bucket_color(
    value: float,
    max_value: float,
    palette: tuple[str, ...],
    steps: Sequence[float] | None = None,
) -> str:
    """Map a value to a palette color.

    Without custom ``steps``, retain Quilt original automatic scale. With
    ``steps``, require five absolute intensity levels, one per palette color.
    """
    if steps is None:
        if value <= 0 or max_value <= 0:
            return palette[0]
        width = max_value / (len(palette) - 1)
        index = min(len(palette) - 1, int(value / width) + 1)
        return palette[index]

    levels = resolve_steps(max_value, steps)
    return color_for_steps(value, levels, palette)
