
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from knowledge_base import KnowledgeBase
from simulated_player import SimulatedPlayer


data_path = (
    Path(__file__).parent.parent
    / "data"
    / "raw"
    / "knowledge_base.csv"
)

kb = KnowledgeBase.from_csv(data_path)

secret = kb.candidate(kb.candidate_index("Imran Khan"))

rng = np.random.default_rng(42)

player = SimulatedPlayer(
    secret=secret,
    noise_rate=0.05,
    rng=rng
)

question = kb.attribute_index("is_cricketer")

for i in range(10):
    print(player.answer(question))
