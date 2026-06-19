"""Shared loader for labeled evaluation fixtures."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

VerdictLabel = Literal["true", "false"]
ClaimType = Literal["political", "scientific", "statistical"]

DEFAULT_FIXTURE = Path(__file__).parent / "fixtures" / "labeled_claims.json"


@dataclass
class LabeledClaim:
    claim: str
    label: VerdictLabel
    category: str = "general"
    claim_type: ClaimType = "scientific"
    url: str | None = None
    tags: list[str] = field(default_factory=list)

    @property
    def use_social_pipeline(self) -> bool:
        return self.category == "social_url" or bool(self.url)

    @property
    def is_adversarial(self) -> bool:
        return "adversarial" in self.tags or "well_sourced_lie" in self.tags


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
                claim_type=row.get("claim_type", "scientific"),
                url=row.get("url"),
                tags=list(row.get("tags", [])),
            )
        )
    return items
