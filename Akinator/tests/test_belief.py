import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from belief import ANSWERS, BeliefState  # noqa: E402
from knowledge_base import KnowledgeBase  # noqa: E402


@pytest.fixture
def tiny_kb():
    # 3 candidates x 2 attributes
    return KnowledgeBase(
        ["A", "B", "C"],
        ["is_person", "is_alive"],
        np.array([[1, 1], [1, 0], [0, 0]], dtype=float),
    )


@pytest.fixture
def real_kb():
    return KnowledgeBase.from_csv(ROOT / "data" / "raw" / "knowledge_base.csv")


def test_uniform_prior(tiny_kb):
    b = BeliefState(tiny_kb)
    assert np.allclose(b.probs, 1 / 3)
    assert b.entropy() == pytest.approx(np.log2(3))


def test_yes_raises_candidates_with_attribute(tiny_kb):
    b = BeliefState(tiny_kb)
    b.update("is_person", "yes")
    assert b.probs[0] > 1 / 3 and b.probs[1] > 1 / 3 and b.probs[2] < 1 / 3
    assert b.probs.sum() == pytest.approx(1.0)


def test_no_raises_candidates_without_attribute(tiny_kb):
    b = BeliefState(tiny_kb)
    b.update("is_person", "no")
    assert b.probs[2] > b.probs[0]


def test_dont_know_changes_nothing(tiny_kb):
    b = BeliefState(tiny_kb)
    b.update("is_alive", "dont_know")
    assert np.allclose(b.probs, 1 / 3)


def test_probably_is_weaker_than_yes(tiny_kb):
    strong, weak = BeliefState(tiny_kb), BeliefState(tiny_kb)
    strong.update("is_alive", "yes")
    weak.update("is_alive", "probably")
    assert strong.probs[0] > weak.probs[0] > 1 / 3


def test_one_wrong_answer_does_not_eliminate_truth(tiny_kb):
    b = BeliefState(tiny_kb)
    b.update("is_alive", "no")      # wrong for secret "A"
    assert b.probs[0] > 0           # still possible
    b.update("is_person", "yes")
    b.update("is_alive", "yes")     # player corrects themselves
    assert b.best()[0] == "A"


def test_posterior_does_not_mutate(tiny_kb):
    b = BeliefState(tiny_kb)
    before = b.probs.copy()
    b.posterior("is_person", "yes")
    assert np.array_equal(b.probs, before) and b.asked == []


def test_predictive_is_distribution(real_kb):
    b = BeliefState(real_kb)
    for j in range(real_kb.n_attributes):
        pred = b.predictive(j)
        assert pred.shape == (len(ANSWERS),)
        assert pred.sum() == pytest.approx(1.0)


def test_predictive_matches_posterior_average(tiny_kb):
    """Law of total probability: sum_a P(a) * posterior(a) == prior."""
    b = BeliefState(tiny_kb)
    pred = b.predictive("is_alive")
    mix = sum(pred[i] * b.posterior("is_alive", a) for i, a in enumerate(ANSWERS))
    assert np.allclose(mix, b.probs)


def test_top_k_sorted(real_kb):
    b = BeliefState(real_kb)
    b.update("is_person", "yes")
    b.update("is_cricketer", "yes")
    probs = [p for _, p in b.top_k(5)]
    assert probs == sorted(probs, reverse=True)


def test_knowledge_base_has_no_indistinguishable_candidates(real_kb):
    assert real_kb.duplicate_groups() == []


def test_noiseless_game_finds_every_candidate(real_kb):
    """Greedy sanity check: answering truthfully should identify each secret."""
    for secret in range(real_kb.n_candidates):
        b = BeliefState(real_kb)
        for _ in range(25):
            if b.is_confident(0.85):
                break
            # pick the attribute whose predictive distribution is least lopsided
            best = max(
                b.unasked_attributes(),
                key=lambda j: 1 - abs(b.predictive(j)[0] + b.predictive(j)[1]
                                       - b.predictive(j)[3] - b.predictive(j)[4]),
            )
            v = real_kb.matrix[secret, best]
            b.update(best, "yes" if v >= 0.5 else "no")
        assert b.best()[0] == real_kb.names[secret]


def test_add_candidate(real_kb):
    n = real_kb.n_candidates
    i = real_kb.add_candidate("Test Person", {"is_person": "yes", "is_alive": "probably"})
    assert real_kb.n_candidates == n + 1
    assert real_kb.value(i, "is_person") == 1.0
    assert real_kb.value(i, "is_alive") == 0.75
    assert real_kb.value(i, "is_cricketer") == 0.5
    with pytest.raises(ValueError):
        real_kb.add_candidate("Test Person")
