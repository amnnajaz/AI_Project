
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from knowledge_base import KnowledgeBase
from evaluator import Evaluator


project_root = Path(__file__).parent.parent

data_path = (
    project_root
    / "data"
    / "raw"
    / "knowledge_base.csv"
)

kb = KnowledgeBase.from_csv(data_path)

evaluator = Evaluator(
    kb=kb,
    noise_levels=(0.0,),
    runs_per_candidate=1,
    seed=42
)

print("Running test experiments...")

results = evaluator.run_experiments()

print("\nExperiment results:")
print(results.head())

print("\nEvaluation metrics:")
print(evaluator.compute_metrics())

evaluator.save_results()
evaluator.plot_charts()

print("\nTest completed!")
