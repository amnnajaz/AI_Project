"""Belief state and Bayesian update for "Guess Who I Am".

The agent keeps a probability distribution over all candidates. After each
question the player's answer (one of five options) updates it with Bayes' rule:

    P(candidate | answer)  ∝  P(answer | candidate) * P(candidate)

Likelihood model (soft, so "Probably" and mistaken answers are tolerated)
-----------------------------------------------------------------------
Each candidate has an attribute value v in [0, 1] (1 = true, 0 = false).
A player answers according to the table below. Each column sums to 1, so it is
a proper probability distribution over the five answers.

    answer          attribute TRUE   attribute FALSE
    yes                  0.55             0.04
    probably             0.25             0.06
    dont_know            0.10             0.10
    probably_not         0.06             0.25
    no                   0.04             0.55

For a candidate with fractional v the likelihood is the mixture
    P(a | candidate) = v * P(a | true) + (1 - v) * P(a | false).

Because no entry is zero, a single wrong answer can never eliminate the
true candidate; it only lowers its probability, and later answers can recover.
"Don't know" has the same likelihood in both columns, so it changes nothing.
"""
from __future__ import annotations

import numpy as np

from knowledge_base import KnowledgeBase

ANSWERS: tuple[str, ...] = ("yes", "probably", "dont_know", "probably_not", "no")

# Rows follow ANSWERS; column 0 = attribute false, column 1 = attribute true.
DEFAULT_LIKELIHOOD = np.array(
    [
        [0.04, 0.55],  # yes
        [0.06, 0.25],  # probably
        [0.10, 0.10],  # dont_know
        [0.25, 0.06],  # probably_not
        [0.55, 0.04],  # no
    ]
)


def _answer_index(answer: str | int) -> int:
    if isinstance(answer, (int, np.integer)):
        if not 0 <= answer < len(ANSWERS):
            raise ValueError(f"answer index out of range: {answer}")
        return int(answer)
    try:
        return ANSWERS.index(answer)
    except ValueError:
        raise ValueError(f"answer must be one of {ANSWERS}, got {answer!r}") from None


class BeliefState:
    """Probability distribution over the candidates of a KnowledgeBase."""

    def __init__(
        self,
        kb: KnowledgeBase,
        prior: np.ndarray | None = None,
        likelihood: np.ndarray | None = None,
    ):
        self.kb = kb
        self.likelihood = DEFAULT_LIKELIHOOD if likelihood is None else np.asarray(likelihood, float)
        if self.likelihood.shape != (len(ANSWERS), 2):
            raise ValueError("likelihood must have shape (5, 2)")
        if not np.allclose(self.likelihood.sum(axis=0), 1.0):
            raise ValueError("each likelihood column must sum to 1")
        if prior is None:
            self.probs = np.full(kb.n_candidates, 1.0 / kb.n_candidates)
        else:
            prior = np.asarray(prior, float)
            if prior.shape != (kb.n_candidates,) or prior.min() < 0 or prior.sum() <= 0:
                raise ValueError("prior must be a non-negative vector with one entry per candidate")
            self.probs = prior / prior.sum()
        self.asked: list[int] = []              # attribute indices, in order
        self.answers: list[str] = []            # answers given, in order

    # ------------------------------------------------------------------ #
    # Likelihoods
    # ------------------------------------------------------------------ #
    def answer_likelihood(self, attribute: str | int, answer: str | int) -> np.ndarray:
        """P(answer | candidate) for every candidate, shape (n_candidates,)."""
        j = self.kb.attribute_index(attribute)
        a = _answer_index(answer)
        v = self.kb.matrix[:, j]
        return v * self.likelihood[a, 1] + (1.0 - v) * self.likelihood[a, 0]

    # ------------------------------------------------------------------ #
    # Updating
    # ------------------------------------------------------------------ #
    def posterior(self, attribute: str | int, answer: str | int) -> np.ndarray:
        """Posterior over candidates if `answer` were given. Does NOT change state."""
        unnorm = self.probs * self.answer_likelihood(attribute, answer)
        return unnorm / unnorm.sum()

    def update(self, attribute: str | int, answer: str | int) -> None:
        """Apply Bayes' rule in place and remember the question and answer."""
        self.probs = self.posterior(attribute, answer)
        self.asked.append(self.kb.attribute_index(attribute))
        self.answers.append(ANSWERS[_answer_index(answer)])

    def predictive(self, attribute: str | int) -> np.ndarray:
        """P(answer) for each of the 5 answers under the current belief.

        Shape (5,), sums to 1. Used for expected information gain:
            gain = H(current) - sum_a P(a) * H(posterior given a)
        """
        j = self.kb.attribute_index(attribute)
        v = self.kb.matrix[:, j]
        # (5, n) likelihoods weighted by current probabilities.
        per_answer = self.likelihood[:, 1:2] * v + self.likelihood[:, 0:1] * (1.0 - v)
        return per_answer @ self.probs

    # ------------------------------------------------------------------ #
    # Summaries
    # ------------------------------------------------------------------ #
    def entropy(self) -> float:
        """Shannon entropy of the belief, in bits."""
        p = self.probs[self.probs > 0]
        return float(-(p * np.log2(p)).sum())

    def top_k(self, k: int = 5) -> list[tuple[str, float]]:
        """The k most probable candidates as (name, probability), best first."""
        k = min(k, self.kb.n_candidates)
        idx = np.argsort(-self.probs, kind="stable")[:k]
        return [(self.kb.names[i], float(self.probs[i])) for i in idx]

    def best(self) -> tuple[str, float]:
        return self.top_k(1)[0]

    def is_confident(self, threshold: float = 0.85) -> bool:
        return float(self.probs.max()) >= threshold

    def copy(self) -> "BeliefState":
        other = BeliefState(self.kb, likelihood=self.likelihood)
        other.probs = self.probs.copy()
        other.asked = list(self.asked)
        other.answers = list(self.answers)
        return other

    def unasked_attributes(self) -> list[int]:
        """Attribute indices not yet asked (what a question selector chooses from)."""
        done = set(self.asked)
        return [j for j in range(self.kb.n_attributes) if j not in done]
