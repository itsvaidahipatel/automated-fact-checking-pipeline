"""Shared loader for labeled evaluation fixtures."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

VerdictLabel = Literal["true", "false"]

DEFAULT_FIXTURE = Path(__file__).parent / "fixtures" / "labeled_claims.json"


@dataclass
class LabeledClaim:
    claim: str
    label: VerdictLabel
    category: str = "general"
    url: str | None = None

    @property
    def use_social_pipeline(self) -> bool:
        return self.category == "social_url" or bool(self.url)


def load_labeled_claims(path: Path) -> list[LabeledClaim]:
    with path.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    items: list[LabeledClaim] = []
    for row in raw:
        items.append(
            LabeledClaim(
                claim=row["claim"],
                label=row["label"],
                category=row.get("category", "general"),
                url=row.get("url"),
            )
        )
    return items
