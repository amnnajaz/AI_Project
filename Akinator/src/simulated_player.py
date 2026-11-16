
import numpy as np

from belief import ANSWERS
from belief import DEFAULT_LIKELIHOOD


class SimulatedPlayer:
    """Simulates a player with a known secret candidate."""

    def __init__(self, secret, noise_rate=0.0, rng=None):
        if not 0.0 <= noise_rate <= 1.0:
            raise ValueError("noise_rate must be between 0 and 1.")

        self.secret = secret
        self.noise_rate = noise_rate
        self.rng = rng if rng is not None else np.random.default_rng()

    def answer(self, question):
        """Generate an answer for the given attribute index."""

        if not 0 <= question < len(self.secret.values):
            raise ValueError("Invalid question index.")

        attribute_value = self.secret.values[question]

        # Calculate answer probabilities for this candidate.
        probabilities = (
            (1 - attribute_value) * DEFAULT_LIKELIHOOD[:, 0]
            + attribute_value * DEFAULT_LIKELIHOOD[:, 1]
        )

        # Generate an answer using the five-option likelihood model.
        answer_index = self.rng.choice(
            len(ANSWERS),
            p=probabilities
        )

        # Introduce deliberate answer noise.
        if self.rng.random() < self.noise_rate:
            alternatives = [
                i for i in range(len(ANSWERS))
                if i != answer_index
            ]

            answer_index = self.rng.choice(alternatives)

        return ANSWERS[answer_index]
