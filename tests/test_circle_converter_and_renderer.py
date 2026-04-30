import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from circle_converter import build_layout
from json_to_image import _chunk, draw_disc, render_layout, write_png


def test_build_layout_rejects_empty_sigils() -> None:
    with pytest.raises(ValueError, match="At least one sigil"):
        build_layout([])


def test_build_layout_has_expected_top_and_clockwise_order() -> None:
    layout = build_layout(["a", "b", "c", "d"])
    sigils = layout["sigils"]

    assert layout["sigil_count"] == 4
    assert layout["circle"]["rotation"] == "clockwise"
    assert sigils[0]["position"] == {"x": 0.0, "y": 1.0}
    assert sigils[1]["position"] == {"x": 1.0, "y": 0.0}
    assert sigils[2]["position"] == {"x": 0.0, "y": -1.0}
    assert sigils[3]["position"] == {"x": -1.0, "y": 0.0}


def test_build_layout_custom_radius_and_start_angle() -> None:
    layout = build_layout(["solo"], radius=2.5, start_angle_degrees=180.0)
    placement = layout["sigils"][0]

    assert layout["circle"]["radius"] == 2.5
    assert placement["angle_degrees"] == 180.0
    assert placement["position"]["x"] == -2.5
    assert placement["position"]["y"] == 0.0


def test_build_layout_points_lie_on_radius() -> None:
    radius = 3.2
    layout = build_layout([str(i) for i in range(9)], radius=radius)

    for placement in layout["sigils"]:
        x = placement["position"]["x"]
        y = placement["position"]["y"]
        assert math.isclose(math.hypot(x, y), radius, abs_tol=1e-5)


def test_chunk_has_correct_png_chunk_layout() -> None:
    chunk = _chunk(b"IEND", b"")
    assert chunk[:4] == (0).to_bytes(4, "big")
    assert chunk[4:8] == b"IEND"
    assert len(chunk) == 12


def test_draw_disc_colors_center_and_skips_far_pixel() -> None:
    width = height = 11
    pixels = bytearray([0, 0, 0, 0] * (width * height))

    draw_disc(pixels, width, height, cx=5, cy=5, radius=2, color=(9, 8, 7, 255))

    center = (5 * width + 5) * 4
    far = (0 * width + 0) * 4
    assert bytes(pixels[center : center + 4]) == b"\x09\x08\x07\xff"
    assert bytes(pixels[far : far + 4]) == b"\x00\x00\x00\x00"


def test_render_layout_returns_expected_row_shapes() -> None:
    payload = build_layout(["a", "b", "c", "d"])
    rows = render_layout(payload, size=32)

    assert len(rows) == 32
    assert all(len(row) == 32 * 4 for row in rows)


def test_render_layout_raises_when_sigils_key_missing() -> None:
    with pytest.raises(KeyError):
        render_layout({"circle": {}}, size=16)


def test_write_png_produces_png_signature(tmp_path: Path) -> None:
    rows = [b"\x00\x00\x00\xff" * 4 for _ in range(4)]
    out = tmp_path / "tiny.png"

    write_png(out, rows, width=4, height=4)

    data = out.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert b"IHDR" in data and b"IDAT" in data and b"IEND" in data


def test_cli_circle_converter_pretty_prints_json() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(repo_root / "circle_converter.py"), "foo", "bar", "--pretty"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["sigil_count"] == 2
    assert "\n" in result.stdout


def test_cli_json_to_image_generates_file(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[1]
    input_json = tmp_path / "layout.json"
    output_png = tmp_path / "layout.png"
    payload = build_layout(["a", "b", "c"])
    input_json.write_text(json.dumps(payload))

    subprocess.run(
        [
            sys.executable,
            str(repo_root / "json_to_image.py"),
            str(input_json),
            str(output_png),
            "--size",
            "64",
        ],
        check=True,
    )

    assert output_png.exists()
    assert output_png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
