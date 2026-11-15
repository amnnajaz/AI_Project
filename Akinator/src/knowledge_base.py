"""Knowledge base for "Guess Who I Am".

Each candidate (a Pakistani personality or place) is described by a vector of
attribute values in [0, 1]:

    1.0  -> the attribute is definitely true for this candidate
    0.0  -> the attribute is definitely false
    0.5  -> unknown (used for characters added by the player at run time)

Values are floats (not just 0/1) so the belief update can treat uncertain
facts correctly. The whole table is exposed as a NumPy matrix `kb.matrix`
of shape (n_candidates, n_attributes) so selectors can work in bulk.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

# Natural-language question for each attribute (used by the UI).
QUESTIONS: dict[str, str] = {
    "is_person": "Is it a person?",
    "is_place": "Is it a place?",
    "is_alive": "Is this person alive today?",
    "is_male": "Is it a man?",
    "is_female": "Is it a woman?",
    "born_before_1950": "Was this person born before 1950?",
    "active_in_21st_century": "Was this person active after the year 2000?",
    "is_politician": "Is this person a politician?",
    "was_prime_minister": "Has this person been Prime Minister of Pakistan?",
    "was_president": "Has this person been President (or head of state) of Pakistan?",
    "is_military_figure": "Is this person from the military?",
    "is_cricketer": "Is this person a cricketer?",
    "is_fast_bowler": "Was this person a fast bowler?",
    "captained_national_team": "Has this person captained Pakistan in cricket?",
    "is_other_sportsperson": "Is this person a sportsperson in a sport other than cricket?",
    "is_actor_or_filmmaker": "Is this person an actor or filmmaker?",
    "is_singer_or_musician": "Is this person a singer or musician?",
    "is_writer_or_poet": "Is this person a writer or poet?",
    "is_scientist_or_academic": "Is this person a scientist or academic?",
    "is_activist_or_humanitarian": "Is this person an activist or humanitarian?",
    "is_businessperson": "Is this person a businessperson?",
    "is_tv_personality": "Is this person a TV/media personality?",
    "won_international_award": "Has it won a major international award (e.g. Nobel, Oscar, Olympic gold)?",
    "is_known_internationally": "Is it famous outside Pakistan?",
    "linked_to_pakistan_movement": "Is it linked to the creation of Pakistan?",
    "region_punjab": "Is it from (or located in) Punjab?",
    "region_sindh": "Is it from (or located in) Sindh?",
    "region_kpk": "Is it from (or located in) Khyber Pakhtunkhwa?",
    "region_balochistan": "Is it from (or located in) Balochistan?",
    "region_islamabad_gb_ajk": "Is it from (or located in) Islamabad, Gilgit-Baltistan or Azad Kashmir?",
    "is_city": "Is it a city?",
    "is_capital_city": "Is it a national or provincial capital?",
    "is_historical_monument": "Is it a historical monument or building?",
    "is_religious_site": "Is it a religious site?",
    "is_mosque": "Is it a mosque?",
    "is_shrine_or_tomb": "Is it a shrine or a tomb?",
    "is_fort_or_palace": "Is it a fort or a palace?",
    "is_natural_landmark": "Is it a natural landmark?",
    "is_peak": "Is it a mountain peak?",
    "is_lake": "Is it a lake?",
    "is_valley_or_meadow": "Is it a valley or a meadow?",
    "is_unesco_world_heritage": "Is it a UNESCO World Heritage Site?",
    "is_coastal": "Is it on the coast?",
    "is_in_mountains": "Is it in the mountains?",
    "is_tourist_destination": "Is it a popular tourist destination?",
    "is_known_for_food": "Is it especially known for its food?",
    "is_mughal_era": "Does it date from (or is it associated with) the Mughal era?",
}

# How a player's answer is turned into an attribute value when a NEW
# character is added after a wrong guess. Unanswered questions stay at 0.5.
ANSWER_TO_VALUE: dict[str, float] = {
    "yes": 1.0,
    "probably": 0.75,
    "dont_know": 0.5,
    "probably_not": 0.25,
    "no": 0.0,
}


@dataclass(frozen=True)
class Candidate:
    """One row of the knowledge base."""

    name: str
    values: tuple[float, ...]  # aligned with KnowledgeBase.attributes


class KnowledgeBase:
    """Table of candidates x attributes backed by a NumPy matrix."""

    def __init__(self, names: list[str], attributes: list[str], matrix: np.ndarray):
        matrix = np.asarray(matrix, dtype=float)
        if matrix.shape != (len(names), len(attributes)):
            raise ValueError(
                f"matrix shape {matrix.shape} does not match "
                f"({len(names)} names, {len(attributes)} attributes)"
            )
        if matrix.size and (matrix.min() < 0.0 or matrix.max() > 1.0):
            raise ValueError("attribute values must lie in [0, 1]")
        if len(set(names)) != len(names):
            raise ValueError("candidate names must be unique")
        self.names: list[str] = list(names)
        self.attributes: list[str] = list(attributes)
        self.matrix: np.ndarray = matrix
        self._attr_index = {a: i for i, a in enumerate(self.attributes)}

    # ------------------------------------------------------------------ #
    # Construction / persistence
    # ------------------------------------------------------------------ #
    @classmethod
    def from_csv(cls, path: str | Path) -> "KnowledgeBase":
        """Load a CSV whose first column is `name` and the rest are attributes."""
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            if header[0] != "name":
                raise ValueError("first CSV column must be 'name'")
            attributes = header[1:]
            names, rows = [], []
            for line_no, row in enumerate(reader, start=2):
                if not row:
                    continue
                if len(row) != len(header):
                    raise ValueError(f"line {line_no}: expected {len(header)} columns")
                names.append(row[0].strip())
                rows.append([float(x) for x in row[1:]])
        return cls(names, attributes, np.array(rows, dtype=float))

    def save_csv(self, path: str | Path) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", *self.attributes])
            for name, row in zip(self.names, self.matrix):
                writer.writerow([name, *[f"{v:g}" for v in row]])

    # ------------------------------------------------------------------ #
    # Basic accessors
    # ------------------------------------------------------------------ #
    def __len__(self) -> int:
        return len(self.names)

    @property
    def n_candidates(self) -> int:
        return len(self.names)

    @property
    def n_attributes(self) -> int:
        return len(self.attributes)

    def attribute_index(self, attribute: str | int) -> int:
        """Accept either an attribute name or an index and return the index."""
        if isinstance(attribute, (int, np.integer)):
            return int(attribute)
        try:
            return self._attr_index[attribute]
        except KeyError:
            raise KeyError(f"unknown attribute: {attribute!r}") from None

    def candidate(self, index: int) -> Candidate:
        return Candidate(self.names[index], tuple(self.matrix[index]))

    def candidate_index(self, name: str) -> int:
        return self.names.index(name)

    def question_text(self, attribute: str | int) -> str:
        name = self.attributes[self.attribute_index(attribute)]
        return QUESTIONS.get(name, f"Does it have the property '{name}'?")

    def value(self, candidate: str | int, attribute: str | int) -> float:
        i = candidate if isinstance(candidate, (int, np.integer)) else self.candidate_index(candidate)
        return float(self.matrix[i, self.attribute_index(attribute)])

    # ------------------------------------------------------------------ #
    # Quality checks and editing
    # ------------------------------------------------------------------ #
    def duplicate_groups(self) -> list[list[str]]:
        """Groups of candidates with identical attribute vectors.

        Such candidates can never be told apart by any question, so these
        should be fixed in the data (or listed as a known limitation).
        """
        groups: dict[tuple, list[str]] = {}
        for name, row in zip(self.names, self.matrix):
            groups.setdefault(tuple(row), []).append(name)
        return [g for g in groups.values() if len(g) > 1]

    def add_candidate(self, name: str, answers: dict[str, str] | None = None) -> int:
        """Add a new character, e.g. after the AI guessed wrongly.

        `answers` maps attribute name -> one of 'yes', 'probably', 'dont_know',
        'probably_not', 'no' (the answers the player gave during the game).
        Attributes the player was never asked about are stored as 0.5.
        Returns the index of the new candidate.
        """
        name = name.strip()
        if not name:
            raise ValueError("name must not be empty")
        if name in self.names:
            raise ValueError(f"{name!r} already exists in the knowledge base")
        row = np.full(self.n_attributes, 0.5)
        for attr, ans in (answers or {}).items():
            row[self.attribute_index(attr)] = ANSWER_TO_VALUE[ans]
        self.names.append(name)
        self.matrix = np.vstack([self.matrix, row])
        return len(self.names) - 1
