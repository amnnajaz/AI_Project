
import random
import numpy as np
from abc import ABC, abstractmethod


class QuestionSelector(ABC):
    """Base class for question selection strategies."""

    @abstractmethod
    def select(self, belief, kb, asked=None):
        pass

    def available_questions(self, belief, asked=None):
        """Return attribute indices that have not been asked yet."""
        unavailable = set(belief.asked)

        if asked is not None:
            unavailable.update(asked)

        return [
            j for j in belief.unasked_attributes()
            if j not in unavailable
        ]


class InfoGainSelector(QuestionSelector):
    """Selects questions using expected information gain."""

    def entropy(self, probabilities):
        """Calculate Shannon entropy in bits."""
        probabilities = np.asarray(probabilities, dtype=float)
        probabilities = probabilities[probabilities > 0]

        return float(-np.sum(probabilities * np.log2(probabilities)))

    def expected_information_gain(self, belief, attribute):
        """Calculate expected information gain for one attribute."""

        current_entropy = belief.entropy()
        answer_probabilities = belief.predictive(attribute)

        expected_entropy = 0.0

        for answer_index, probability in enumerate(answer_probabilities):

            if probability <= 0:
                continue

            posterior = belief.posterior(attribute, answer_index)

            expected_entropy += (
                probability * self.entropy(posterior)
            )

        return max(0.0, current_entropy - expected_entropy)

    def select(self, belief, kb, asked=None):
        """Return the attribute index with the highest information gain."""

        available = self.available_questions(belief, asked)

        if not available:
            raise ValueError("No unused questions available.")

        scores = {
            attribute: self.expected_information_gain(
                belief, attribute
            )
            for attribute in available
        }

        return max(scores, key=scores.get)


class RandomSelector(QuestionSelector):
    """Selects a random unused question as the baseline."""

    def __init__(self, seed=42):
        self.rng = random.Random(seed)

    def select(self, belief, kb, asked=None):
        """Return a randomly selected unused attribute index."""

        available = self.available_questions(belief, asked)

        if not available:
            raise ValueError("No unused questions available.")

        return self.rng.choice(available)
