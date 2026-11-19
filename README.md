## Guess Who I Am (Akinator-Style)

**AL-2002 Artificial Intelligence (Laboratory) · Fall 2026 · FAST-NUCES, Karachi Campus**

"Guess Who I Am" is an Akinator-style game in which the player secretly thinks of a well-known Pakistani personality or place, and the computer works out who or what it is by asking yes/no questions. After every answer, the program updates how likely each candidate is (Bayesian belief updating with soft likelihoods, so "Probably" and even mistaken answers are tolerated) and then asks the question with the highest expected information gain, meaning the one that reduces uncertainty the most. The agent is utility-based and reasons under uncertainty rather than following a fixed script. Its performance is evaluated against a random-question baseline using a simulated player at different noise levels.

## Team

| Member | Roll No. | Section | What they built |
|---|---|---|---|
| Amnn Jindani (Leader) | 24K-2584 | BDS-5A | Knowledge base, Belief State and Bayesian update, unit tests, and the project report. |
| Farwa Batool Naqvi | 24L-2508 | BDS-5A | Question selectors (information gain and random baseline), Streamlit UI, SimulatedPlayer, Evaluator and charts. |

## Repository Structure

All project files live in the `Akinator/` folder of the `AI_Project` repository.

```
AI_Project/
├── README.md
└── Akinator/
    ├── README.md
    ├── requirements.txt
    ├── .gitignore
    │
    ├── docs/
    │   ├── proposal.md
    │   ├── proposal.pdf
    │   ├── report.md
    │   └── report.pdf
    │
    ├── src/
    │   ├── knowledge_base.py
    │   ├── belief.py
    │   ├── question_selector.py
    │   ├── game_agent.py
    │   ├── simulated_player.py
    │   ├── evaluator.py
    │   └── app.py
    │
    ├── tests/
    │   └── test_evaluator.py
    │   ├── test_belief.py
    │   ├── test_game_agent.py
    │   └──  test_simulated_player.py
    │
    ├── data/
    │   └── raw/
    │       └── knowledge_base.csv
    |   └── build_knowledge_base.py
    │
    └── outputs/
        ├── experiment_results.csv
        ├── evaluation_metrics.csv
        ├── success_rate.png
        ├── average_questions.png
        ├── question_distribution.png
        └── entropy_progression.png
```

## Setup

Requires Python 3.10 to 3.12.

```bash
# 1. Clone the repository and enter the project folder
git clone https://github.com/amnnajaz/AI_Project.git
cd AI_Project/Akinator

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: .\venv\Scripts\Activate.ps1

# 3. Install the dependencies
pip install -r requirements.txt
```

No API keys or internet connection are needed to run the project: the knowledge base is stored locally in `data/raw/knowledge_base.csv`.

## How to Run

Run all commands from inside the `Akinator/` folder.

**Play the game (Streamlit app):**

```bash
streamlit run src/app.py
```

Think of a Pakistani personality or place, then answer each question with Yes / Probably / Don't know / Probably not / No. The app shows the current top guesses with their probabilities and makes a final guess once it is confident (top probability ≥ 0.85) or after 20 questions.

**Run the unit tests:**

```bash
python -m pytest tests -q
```

## How the Belief Update Works

The agent keeps a probability for every candidate. After each answer it applies Bayes' rule:

`P(candidate | answer) ∝ P(answer | candidate) × P(candidate)`

The likelihood of each answer depends on whether the candidate has the asked attribute:

| Answer | Attribute true | Attribute false |
|---|---|---|
| Yes | 0.55 | 0.04 |
| Probably | 0.25 | 0.06 |
| Don't know | 0.10 | 0.10 |
| Probably not | 0.06 | 0.25 |
| No | 0.04 | 0.55 |

No entry is zero, so one mistaken answer lowers the true candidate's probability but never eliminates it, and later answers can recover it. "Don't know" has the same likelihood in both columns, so it leaves the belief unchanged. Attribute values may also be fractional (for example, characters added during play start at 0.5 for questions never asked), in which case the likelihood is the corresponding mixture of the two columns.

## Reproducing the Experiments

```bash
python src/evaluate.py --seed 42 --runs 10 --noise 0.0 0.05 0.10
```

This uses every candidate in the knowledge base as the secret for a simulated player, with 10 runs per candidate at 0%, 5% and 10% answer noise (fixed seed 42), and compares information-gain question selection against the random-question baseline. Results are written to `outputs/results/` and charts to `outputs/figures/`:

1. Success rate by approach and noise level
2. Average questions to guess versus noise
3. Distribution of questions needed
4. Entropy versus question number

## Features

- Knowledge base of Pakistani personalities and places described by about 47 yes/no attributes (see "Data Source" for the current size)
- Bayesian belief update supporting five answer options (Yes, Probably, Don't know, Probably not, No)
- Information-gain (expected entropy reduction) question selection
- Streamlit game interface showing live top guesses with probabilities
- Automated evaluation against a random-question baseline using a noisy simulated player
- Ability to add a new character when the AI guesses incorrectly
- Unit tests for the knowledge base and the belief update

## Known Limitations

- Text-only, button-based input: no free-text or voice input.
- English only (no Urdu support).
- Single-player, with no multiplayer or leaderboard features.
- The knowledge base is hand-curated and limited in size, so some characters are missing and some questions may split candidates poorly.
- No live web scraping; the data is static unless updated manually.
- Not packaged as a mobile app.

## Data Source

`data/raw/knowledge_base.csv` is a self-collected, hand-curated dataset compiled from public facts (e.g. Wikipedia and Wikidata, https://www.wikidata.org). Wikidata facts are CC0 and no Wikipedia text is copied. The file currently has 92 rows × 47 attribute columns (under 1 MB) and is loaded locally, so no network access is needed at runtime.

The CSV is generated from the compact tag list in `data/build_knowledge_base.py`. To add or edit characters, change the list in that script and run `python data/build_knowledge_base.py`, which rewrites the CSV and warns if two characters cannot be told apart by any question.
