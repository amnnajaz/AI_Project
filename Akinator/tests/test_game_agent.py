
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from knowledge_base import KnowledgeBase
from question_selector import InfoGainSelector
from game_agent import GameAgent

data_path = (
    Path(__file__).parent
    / "data"
    / "raw"
    / "knowledge_base.csv"
)

kb = KnowledgeBase.from_csv(data_path)

agent = GameAgent(
    kb=kb,
    selector=InfoGainSelector()
)

print("Starting game...\n")

while not agent.is_done():

    question_index = agent.ask()

    question_text = kb.question_text(question_index)

    print("Question:", question_text)

    answer = input(
        "Answer (yes/probably/dont_know/probably_not/no): "
    ).strip().lower()

    agent.receive_answer(answer)

    print("Questions asked:", len(agent.belief.asked))
    print("Current best guess:", agent.guess().name)
    print()

print("Game stopped.")
print("Final guess:", agent.guess().name)
print("Final probability:", round(float(agent.belief.probs.max()), 4))
