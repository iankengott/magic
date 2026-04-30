import argparse
import json
import math
import struct
import subprocess
import zlib
from pathlib import Path


def _chunk(chunk_type: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
    return struct.pack('>I', len(data)) + chunk_type + data + struct.pack('>I', crc)


def _write_png(path: Path, rgba_rows: list[bytes], width: int, height: int) -> None:
    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    raw = b''.join(b'\x00' + row for row in rgba_rows)
    idat = zlib.compress(raw, level=9)
    png = signature + _chunk(b'IHDR', ihdr) + _chunk(b'IDAT', idat) + _chunk(b'IEND', b'')
    path.write_bytes(png)


def _draw_disc(
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


def build_sigil_circle_png(output_path: Path, sigil_limit: int = 8, size: int = 256) -> Path:
    sigil_dir = Path('assets/sigils')
    sigils = sorted(p.stem for p in sigil_dir.glob('*.svg'))[:sigil_limit]
    if not sigils:
        raise ValueError('Expected svg sigils in assets/sigils.')

    result = subprocess.run(
        ['python3', 'circle_converter.py', *sigils],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    width = height = size
    pixels = bytearray([18, 18, 24, 255] * (width * height))

    cx = cy = size // 2
    radius_px = int(size * 0.35)

    for t in range(360):
        a = math.radians(t)
        x = int(cx + radius_px * math.cos(a))
        y = int(cy - radius_px * math.sin(a))
        _draw_disc(pixels, width, height, x, y, radius=1, color=(90, 90, 120, 255))

    for placement in payload['sigils']:
        x_norm = placement['position']['x']
        y_norm = placement['position']['y']
        x = int(cx + x_norm * radius_px)
        y = int(cy - y_norm * radius_px)
        _draw_disc(pixels, width, height, x, y, radius=5, color=(235, 220, 120, 255))

    rows = [bytes(pixels[y * width * 4 : (y + 1) * width * 4]) for y in range(height)]
    _write_png(output_path, rows, width, height)
    return output_path


def test_sigils_and_json_maker_create_circle_png(tmp_path: Path) -> None:
    out_path = build_sigil_circle_png(tmp_path / 'sigil_circle.png')
    assert out_path.exists()
    assert out_path.read_bytes().startswith(b'\x89PNG\r\n\x1a\n')


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Create a sigil circle PNG from circle_converter JSON output.')
    parser.add_argument('--output', default='sigil_circle.png', help='Output PNG path (default: sigil_circle.png)')
    parser.add_argument('--sigil-limit', type=int, default=8, help='Number of sigils to place (default: 8)')
    parser.add_argument('--size', type=int, default=256, help='Square image size in pixels (default: 256)')
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    output = build_sigil_circle_png(Path(args.output), sigil_limit=args.sigil_limit, size=args.size)
    print(f'Wrote PNG: {output.resolve()}')


if __name__ == '__main__':
    main()
