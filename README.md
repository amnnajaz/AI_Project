# Guess Who I Am (Akinator-Style)

**AL-2002 Artificial Intelligence (Laboratory) · Fall 2026 · FAST-NUCES, Karachi Campus**

"Guess Who I Am" is an Akinator-style game in which the player secretly thinks of a well-known Pakistani personality or place, and the computer works out who or what it is by asking yes/no questions. After every answer, the program updates how likely each candidate is (Bayesian belief updating with soft likelihoods, so "Probably" and even mistaken answers are tolerated) and then asks the question with the highest expected information gain, meaning the one that reduces uncertainty the most. The agent is utility-based and reasons under uncertainty rather than following a fixed script. Its performance is evaluated against a random-question baseline using a simulated player at different noise levels.

## Team

| Member | Roll No. | Section | What they built |
|---|---|---|---|
| Amnn Jindani (Leader) | 24K-2584 | BDS-5A | Knowledge base, Belief State and Bayesian update, and the project report. |
| Farwa Batool Naqvi | 24L-2508 | BDS-5A | Question selectors (information gain and random baseline), Streamlit UI, SimulatedPlayer, Evaluator and charts. |

## Repository Structure

```
AI_Project/
├── README.md
├── requirements.txt        <- every dependency, pinned
├── .gitignore              <- keeps caches, venvs and secrets out
├── docs/                   <- proposal and report, each as PDF and MD
├── src/                    <- all source code, in modules
│   ├── knowledge_base.py   <- Candidate, KnowledgeBase (loads the CSV)
│   ├── belief.py           <- BeliefState (Bayesian update, entropy, top_k)
│   ├── selectors.py        <- QuestionSelector, InfoGainSelector, RandomSelector
│   ├── agent.py            <- GameAgent
│   ├── simulated_player.py <- SimulatedPlayer (noisy answers)
│   ├── evaluate.py         <- Evaluator (experiments, metrics, charts)
│   └── app.py              <- Streamlit user interface
├── data/
│   ├── raw/                <- knowledge_base.csv
│   └── processed/
└── outputs/
    ├── figures/            <- charts used in the report
    └── results/            <- experiment tables and logs
```

## Setup

Requires Python 3.10 or newer.

```bash
# 1. Clone the repository
git clone https://github.com/amnnajaz/AI_Project.git
cd AI_Project

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install the pinned dependencies
pip install -r requirements.txt
```

No API keys or internet connection are needed to run the project: the knowledge base is stored locally in `data/raw/knowledge_base.csv`.

## How to Run

**Play the game (Streamlit app):**

```bash
streamlit run src/app.py
```

Think of a Pakistani personality or place, then answer each question with Yes / Probably / Don't know / Probably not / No. The app shows the current top guesses with their probabilities and makes a final guess once it is confident (top probability ≥ 0.85) or after 20 questions.

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

- Knowledge base of about 150–200 Pakistani personalities and places described by about 40 yes/no attributes
- Bayesian belief update supporting five answer options (Yes, Probably, Don't know, Probably not, No)
- Information-gain (expected entropy reduction) question selection
- Streamlit game interface showing live top guesses with probabilities
- Automated evaluation against a random-question baseline using a noisy simulated player
- Ability to add a new character when the AI guesses incorrectly

## Known Limitations

- Text-only, button-based input: no free-text or voice input.
- English only (no Urdu support).
- Single-player, with no multiplayer or leaderboard features.
- The knowledge base is hand-curated and limited in size, so some characters are missing and some questions may split candidates poorly.
- No live web scraping; the data is static unless updated manually.
- Not packaged as a mobile app.

## Data Source

`data/raw/knowledge_base.csv` is a self-collected, hand-curated dataset compiled from public facts (e.g. Wikipedia and Wikidata, https://www.wikidata.org). Wikidata facts are CC0 and no Wikipedia text is copied. The file is about 150–200 rows × 40 attribute columns (under 1 MB) and is loaded locally, so no network access is needed at runtime.
