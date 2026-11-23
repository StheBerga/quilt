
import pytest

from habit_heatmap.cli import main


def _write_csv(tmp_path):
    csv_file = tmp_path / "activities.csv"
    csv_file.write_text(
        "date,minutes\n"
        "2024-01-01,5\n"
        "2024-01-02,15\n"
        "2024-01-03,30\n",
        encoding="utf-8",
    )
    return csv_file


def test_cli_accepts_single_step_width(tmp_path):
    csv_file = _write_csv(tmp_path)
    output = tmp_path / "heatmap.svg"

    result = main([
        str(csv_file),
        "--output", str(output),
        "--value-col", "minutes",
        "--steps", "10",
    ])

    assert result == 0
    assert output.exists()
    assert output.read_text(encoding="utf-8").startswith("<svg")


def test_cli_accepts_four_custom_steps(tmp_path):
    csv_file = _write_csv(tmp_path)
    output = tmp_path / "heatmap.svg"

    result = main([
        str(csv_file),
        "--output", str(output),
        "--value-col", "minutes",
        "--steps", "5,15,30,60",
    ])

    assert result == 0
    assert output.exists()


def test_cli_accepts_custom_steps_with_other_options(tmp_path):
    csv_file = _write_csv(tmp_path)
    output = tmp_path / "heatmap.svg"

    result = main([
        str(csv_file),
        "--output", str(output),
        "--value-col", "minutes",
        "--steps", "5,15,30,60",
        "--theme", "blue",
        "--label", "Running activity",
        "--week-start", "monday",
    ])

    assert result == 0
    assert output.exists()
    assert "Running activity" in output.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "steps",
    [
        "0",
        "-5",
        "nan",
        "inf",
    ],
)
def test_cli_rejects_non_positive_or_non_finite_steps(
    tmp_path,
    steps,
):
    csv_file = _write_csv(tmp_path)
    output = tmp_path / "heatmap.svg"

    result = main([
        str(csv_file),
        "--output", str(output),
        "--steps", steps,
    ])

    assert result == 1
    assert not output.exists()


@pytest.mark.parametrize(
    "steps",
    [
        "5,15",
        "5,15,30",
        "5,15,30,60,90",
        "abc",
    ],
)
def test_cli_rejects_malformed_steps(
    tmp_path,
    steps,
):
    csv_file = _write_csv(tmp_path)
    output = tmp_path / "heatmap.svg"

    with pytest.raises(SystemExit) as exc_info:
        main([
            str(csv_file),
            "--output", str(output),
            "--steps", steps,
        ])

    assert exc_info.value.code == 2
    assert not output.exists()



# PNG integration tests require the optional CairoSVG dependency.
@pytest.fixture
def cairosvg_available():
    """Skip PNG tests when CairoSVG or its native dependency is unavailable."""
    try:
        __import__("cairosvg")
    except (ImportError, OSError) as exc:
        pytest.skip(
            f"PNG support requires a working CairoSVG installation: {exc}"
        )


def test_cli_renders_png_with_default_steps(tmp_path, cairosvg_available):
    csv_file = _write_csv(tmp_path)
    output = tmp_path / "heatmap.png"

    result = main([
        str(csv_file),
        "--output", str(output),
        "--value-col", "minutes",
    ])

    assert result == 0
    assert output.exists()
    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_cli_renders_png_with_single_step_width(tmp_path, cairosvg_available):
    csv_file = _write_csv(tmp_path)
    output = tmp_path / "heatmap.png"

    result = main([
        str(csv_file),
        "--output", str(output),
        "--value-col", "minutes",
        "--steps", "10",
    ])

    assert result == 0
    assert output.exists()
    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_cli_renders_png_with_custom_steps(tmp_path, cairosvg_available):
    csv_file = _write_csv(tmp_path)
    output = tmp_path / "heatmap.png"

    result = main([
        str(csv_file),
        "--output", str(output),
        "--value-col", "minutes",
        "--steps", "5,15,30,60",
    ])

    assert result == 0
    assert output.exists()
    assert output.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
