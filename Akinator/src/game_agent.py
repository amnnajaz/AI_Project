
from belief import BeliefState


class GameAgent:
    """Connects the belief state with a question selection strategy."""

    def __init__(
        self,
        kb,
        selector,
        max_questions=20,
        confidence_threshold=0.85
    ):
        self.kb = kb
        self.selector = selector
        self.belief = BeliefState(kb)

        self.max_questions = max_questions
        self.confidence_threshold = confidence_threshold

        self.current_question = None

    def ask(self):
        """Select and return the next question's attribute index."""

        if self.is_done():
            return None

        if self.current_question is not None:
            raise RuntimeError("The current question has not been answered.")

        question = self.selector.select(
            self.belief,
            self.kb
        )

        self.current_question = question

        return question

    def receive_answer(self, answer):
        """Update beliefs using the player's answer."""

        if self.current_question is None:
            raise RuntimeError("Ask a question before receiving an answer.")

        self.belief.update(
            self.current_question,
            answer
        )

        self.current_question = None

    def guess(self):
        """Return the candidate with the highest probability."""

        best_index = self.belief.probs.argmax()

        return self.kb.candidate(best_index)

    def is_done(self):
        """Check whether the game should stop."""

        if len(self.belief.asked) >= self.max_questions:
            return True

        if self.belief.probs.max() >= self.confidence_threshold:
            return True

        return False
