import math

import pytest

from habit_heatmap.colors import THEMES, bucket_color, resolve_steps


def test_bucket_color_zero_value_is_lightest():
    palette = THEMES["github"]
    assert bucket_color(0, 10, palette) == palette[0]


def test_bucket_color_max_value_is_darkest():
    palette = THEMES["github"]
    assert bucket_color(10, 10, palette) == palette[-1]


def test_bucket_color_is_monotonic():
    palette = THEMES["github"]
    low = bucket_color(1, 100, palette)
    high = bucket_color(90, 100, palette)
    assert palette.index(low) < palette.index(high)


def test_bucket_color_handles_zero_max():
    palette = THEMES["github"]
    assert bucket_color(0, 0, palette) == palette[0]


def test_bucket_color_handles_negative_value():
    palette = THEMES["github"]
    assert bucket_color(-5, 10, palette) == palette[0]


def test_default_steps_preserve_four_equal_intervals():
    assert resolve_steps(100) == (25, 50, 75, 100)


def test_numeric_steps_are_repeated_four_times():
    assert resolve_steps(999, 10) == (10, 20, 30, 40)


def test_four_custom_step_widths_are_cumulative():
    assert resolve_steps(999, [5, 15, 30, 60]) == (5, 20, 50, 110)


def test_numeric_steps_use_fixed_color_thresholds():
    palette = THEMES["github"]
    assert bucket_color(9, 100, palette, steps=10) == palette[1]
    assert bucket_color(10, 100, palette, steps=10) == palette[2]
    assert bucket_color(20, 100, palette, steps=10) == palette[3]
    assert bucket_color(30, 100, palette, steps=10) == palette[4]


def test_custom_step_widths_use_cumulative_color_thresholds():
    palette = THEMES["github"]
    steps = [5, 15, 30, 60]  # cumulative limits: 5, 20, 50, 110
    assert bucket_color(4, 999, palette, steps=steps) == palette[1]
    assert bucket_color(5, 999, palette, steps=steps) == palette[2]
    assert bucket_color(19, 999, palette, steps=steps) == palette[2]
    assert bucket_color(20, 999, palette, steps=steps) == palette[3]
    assert bucket_color(50, 999, palette, steps=steps) == palette[4]
    assert bucket_color(150, 999, palette, steps=steps) == palette[4]


@pytest.mark.parametrize("value", [0, -1, math.inf, -math.inf, math.nan])
def test_resolve_steps_rejects_nonpositive_or_nonfinite_scalar(value):
    with pytest.raises(ValueError):
        resolve_steps(100, value)


@pytest.mark.parametrize(
    "values",
    [
        [1, 2, 3],
        [1, 2, 3, 4, 5],
        [1, 2, 0, 4],
        [1, 2, -3, 4],
        [1, 2, math.nan, 4],
        [1, 2, math.inf, 4],
        [1, "not-a-number", 3, 4],
    ],
)
def test_resolve_steps_rejects_invalid_sequences(values):
    with pytest.raises(ValueError):
        resolve_steps(100, values)


def test_resolve_steps_rejects_boolean():
    with pytest.raises(ValueError):
        resolve_steps(100, True)


def test_all_themes_have_five_colors():
    for name, palette in THEMES.items():
        assert len(palette) == 5, name


def test_mono_and_dark_themes_are_registered():
    assert "mono" in THEMES
    assert "dark" in THEMES
