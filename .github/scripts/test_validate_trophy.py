#!/usr/bin/env python3

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_trophy import validate


def trophy_svg(
    *,
    include_multilanguage: bool = True,
    stars_rank: str = "Super Star",
    stars_points: str = "130pt",
    repositories_rank: str = "Super Repo Creator",
    repositories_points: str = "44pt",
) -> str:
    values = []
    if include_multilanguage:
        values.extend(("MultiLanguage", "Rainbow Lang User", "21pt"))
    values.extend(("Stars", stars_rank, stars_points))
    values.extend(("Repositories", repositories_rank, repositories_points))
    text_nodes = "".join(f"<text>{value}</text>" for value in values)
    return f'<svg xmlns="http://www.w3.org/2000/svg">{text_nodes}</svg>'


class ValidateTrophyTests(unittest.TestCase):
    def validate_svg(self, svg: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trophy.svg"
            path.write_text(svg, encoding="utf-8")
            return validate(path)

    def test_accepts_complete_trophy_data(self) -> None:
        self.assertEqual(self.validate_svg(trophy_svg()), [])

    def test_rejects_missing_multilanguage_trophy(self) -> None:
        errors = self.validate_svg(trophy_svg(include_multilanguage=False))
        self.assertIn("missing trophy: MultiLanguage", errors)

    def test_rejects_unknown_stars(self) -> None:
        errors = self.validate_svg(
            trophy_svg(stars_rank="Unknown", stars_points="0pt")
        )
        self.assertIn(
            "invalid trophy data: Stars rank='Unknown' points='0pt'", errors
        )

    def test_rejects_zero_repositories(self) -> None:
        errors = self.validate_svg(
            trophy_svg(repositories_rank="Unknown", repositories_points="0pt")
        )
        self.assertIn(
            "invalid trophy data: Repositories rank='Unknown' points='0pt'", errors
        )

    def test_rejects_malformed_xml(self) -> None:
        errors = self.validate_svg("<svg>")
        self.assertEqual(len(errors), 1)
        self.assertIn("is not valid XML", errors[0])


if __name__ == "__main__":
    unittest.main()
