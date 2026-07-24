#!/usr/bin/env python3
"""Reject incomplete trophy SVGs before they replace the published card."""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


REQUIRED_TITLES = ("MultiLanguage", "Stars", "Repositories")
POINTS_PATTERN = re.compile(r"^(\d+)pt$")


def text_values(root: ET.Element) -> list[str]:
    return [
        (element.text or "").strip()
        for element in root.iter()
        if element.tag.rsplit("}", 1)[-1] == "text" and (element.text or "").strip()
    ]


def validate(path: Path) -> list[str]:
    if not path.is_file() or path.stat().st_size == 0:
        return [f"{path} is missing or empty"]

    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        return [f"{path} is not valid XML: {error}"]

    texts = text_values(root)
    errors: list[str] = []

    for title in REQUIRED_TITLES:
        if title not in texts:
            errors.append(f"missing trophy: {title}")

    for title in ("Stars", "Repositories"):
        if title not in texts:
            continue

        title_index = texts.index(title)
        if title_index + 2 >= len(texts):
            errors.append(f"incomplete trophy: {title}")
            continue

        rank = texts[title_index + 1]
        points = texts[title_index + 2]
        points_match = POINTS_PATTERN.fullmatch(points)
        if rank == "Unknown" or points_match is None or int(points_match.group(1)) == 0:
            errors.append(f"invalid trophy data: {title} rank={rank!r} points={points!r}")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} TROPHY_SVG", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    errors = validate(path)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print("Refusing to replace the last known-good trophy SVG.", file=sys.stderr)
        return 1

    print(f"Validated trophy SVG: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
