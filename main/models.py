from dataclasses import dataclass, field
from typing import List, Dict
import random

TRAIT_CATEGORIES = ["good_morals", "bad_morals", "left_politics", "right_politics", "gaming", "activities", "health", "other", "food"]

@dataclass
class Candidate:
    name: str
    traits: Dict[str, int]
    quote: str
    score: float = 0.0

    @staticmethod
    def random(name: str, quote: str, rng: random.Random) -> "Candidate":
        traits = {k: rng.randint(-2, 2) for k in TRAIT_CATEGORIES}
        return Candidate(name=name, traits=traits, quote=quote)

@dataclass
class Issue:
    text: str
    tags: List[str]
    type: str  # serious | funny | mixed
    weight: float

    @staticmethod
    def from_line(line: str) -> "Issue":
        # Format: text | tags | type | weight
        parts = [p.strip() for p in line.split("|")]
        text = parts[0] if len(parts) > 0 else ""
        tags = []
        typ = "mixed"
        weight = 1.0
        if len(parts) > 1 and parts[1]:
            tags = [t.strip() for t in parts[1].replace(",", ";").split(";") if t.strip()]
        if len(parts) > 2 and parts[2]:
            typ = parts[2].lower()
        if len(parts) > 3 and parts[3]:
            try:
                weight = float(parts[3])
            except ValueError:
                weight = 1.0
        return Issue(text=text, tags=tags, type=typ, weight=weight)
