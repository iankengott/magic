#!/usr/bin/env python3
"""Render circle layout JSON into a simple PNG preview image."""

from __future__ import annotations

import argparse
import json
import math
import struct
import zlib
from pathlib import Path
from typing import Any


def _chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)


def write_png(path: Path, rgba_rows: list[bytes], width: int, height: int) -> None:
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    raw = b"".join(b"\x00" + row for row in rgba_rows)
    idat = zlib.compress(raw, level=9)
    png = signature + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")
    path.write_bytes(png)


def draw_disc(
    pixels: bytearray,
    width: int,
    height: int,
    cx: int,
    cy: int,
    radius: int,
    color: tuple[int, int, int, int],
) -> None:
    r2 = radius * radius
    for y in range(max(0, cy - radius), min(height, cy + radius + 1)):
        for x in range(max(0, cx - radius), min(width, cx + radius + 1)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r2:
                i = (y * width + x) * 4
                pixels[i : i + 4] = bytes(color)


def render_layout(payload: dict[str, Any], size: int = 512) -> list[bytes]:
    width = height = size
    pixels = bytearray([18, 18, 24, 255] * (width * height))

    cx = cy = size // 2
    radius_px = int(size * 0.35)

    for t in range(360):
        a = math.radians(t)
        x = int(cx + radius_px * math.cos(a))
        y = int(cy - radius_px * math.sin(a))
        draw_disc(pixels, width, height, x, y, radius=1, color=(90, 90, 120, 255))

    for placement in payload["sigils"]:
        x_norm = placement["position"]["x"]
        y_norm = placement["position"]["y"]
        x = int(cx + x_norm * radius_px)
        y = int(cy - y_norm * radius_px)
        draw_disc(pixels, width, height, x, y, radius=7, color=(235, 220, 120, 255))

    return [bytes(pixels[y * width * 4 : (y + 1) * width * 4]) for y in range(height)]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render circle JSON into a PNG image.")
    parser.add_argument("input_json", type=Path, help="Path to JSON from circle_converter.py")
    parser.add_argument("output_png", type=Path, help="PNG output path")
    parser.add_argument("--size", type=int, default=512, help="Square output image size (default: 512)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(args.input_json.read_text())
    rows = render_layout(payload, size=args.size)
    write_png(args.output_png, rows, args.size, args.size)


if __name__ == "__main__":
    main()
