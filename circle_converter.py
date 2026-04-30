#!/usr/bin/env python3
"""Convert an ordered list of sigils into evenly spaced magic-circle JSON."""

from __future__ import annotations

import argparse
import json
import math
from typing import Any


def build_layout(sigils: list[str], radius: float = 1.0, start_angle_degrees: float = 90.0) -> dict[str, Any]:
    """Return a JSON-serializable circle layout with each sigil position.

    Sigils are distributed evenly around the center (0, 0).
    """
    if not sigils:
        raise ValueError("At least one sigil is required.")

    step = 360.0 / len(sigils)
    placements = []

    for index, sigil in enumerate(sigils):
        angle_degrees = start_angle_degrees - (index * step)
        angle_radians = math.radians(angle_degrees)
        x = radius * math.cos(angle_radians)
        y = radius * math.sin(angle_radians)

        placements.append(
            {
                "index": index,
                "sigil": sigil,
                "angle_degrees": round(angle_degrees, 6),
                "position": {
                    "x": round(x, 6),
                    "y": round(y, 6),
                },
            }
        )

    return {
        "circle": {
            "center": {"x": 0.0, "y": 0.0},
            "radius": radius,
            "start_angle_degrees": start_angle_degrees,
            "rotation": "clockwise",
        },
        "sigil_count": len(sigils),
        "sigils": placements,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert sigil sequences into JSON with even positions relative to circle center."
    )
    parser.add_argument(
        "sigils",
        nargs="+",
        help="Sigils in casting order (example: 1 2 3 4)",
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=1.0,
        help="Circle radius used for position coordinates (default: 1.0)",
    )
    parser.add_argument(
        "--start-angle",
        type=float,
        default=90.0,
        help="Starting angle in degrees for the first sigil (default: 90, top of circle)",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_layout(args.sigils, radius=args.radius, start_angle_degrees=args.start_angle)
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
