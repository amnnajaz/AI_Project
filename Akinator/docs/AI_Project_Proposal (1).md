

| ![FAST NUCES logo][image1] | FAST — NATIONAL UNIVERSITY OF COMPUTER AND EMERGING SCIENCES FAST School of Computing  ·  Karachi Campus  ·  Department of Artificial Intelligence & Data Science *AL-2002  Artificial Intelligence (Laboratory)  ·  Fall 2026* |
| :---- | :---: |

**PROJECT PROPOSAL**

*Semester Lab Project  ·  Weightage 1 mark*

## **Group Information**

|  | Name | Roll Number | Section | Role in the project |
| :---- | :---- | :---- | :---- | :---- |
| **Leader** | Amnn Jindani | 24K-2584 | BDS-5A | Knowledge Base and Bayesian Belief Updating Developer |
| Member 2 | Farwa Batool Naqvi | 24L-2508 | BDS-5A | Question Selection, User Interface and Evaluation Developer  |

| Project Title | ‘Guess Who I Am’ (Akinator-Style) |
| :---- | :---- |
| **Project Idea** | Idea No. \_\_5\_\_\_\_ from the Project Ideas list           |
| **Category** | Part A — Game            |
| **GitHub Repository URL** | [amnnajaz/AI\_Project: Guess Who I Am](https://github.com/amnnajaz/AI_Project)  |
| **Date of Submission** | 22-10-26 |

# **1\.  Project Title and Summary**

| “Guess Who I Am” is an Akinator-style game in which the player secretly thinks of a well-known Pakistani personality or place, and the computer works out who or what it is by asking yes/no questions. After every answer, the program updates how likely each candidate is and then picks the question that will narrow the field the most. It is meant for anyone curious about Pakistani people, history, and geography, and no prior knowledge is needed to play. A plain program could only follow a fixed script of questions, which fails as soon as the player answers “probably” or gives a mistaken answer. The AI instead reasons under uncertainty, keeps a probability for every candidate and chooses a new best question on every turn. |
| :---- |

# **2\.  Problem Statement and Motivation**

| Identifying a hidden person or place from yes/no answers sounds easy, but the space of possible interrogations is enormous. With a knowledge base of 40 attributes (for example, “is alive”, “is a politician”, “is in Punjab”), the number of ordered ways to choose 20 of them is 40\!/20\!, about 3 × 10^29, so trying every sequence is hopeless. The information is also uncertain: players answer “probably”, misremember facts, or disagree with our data, so a single wrong answer can derail a rigid decision tree. The questions interact too, because a good question depends on every answer already given and on which candidates are still likely. Today, people playing such games simply guess at random or ask questions in a fixed order, which wastes turns and breaks on noisy answers. Solving this is worthwhile because it shows how probability and information theory let a program get the most out of every answer, while making Pakistani culture and geography more interactive to explore. |
| :---- |

# **3\.  Problem Formulation**

## **3.1  PEAS Description**

| Component | Description for your project |
| :---- | :---- |
| **Performance measure** | Success rate (correct guess within 20 questions), average number of questions needed, and robustness when the player gives wrong or uncertain answers. |
| **Environment** | The player, who holds a secret character, and a knowledge base of Pakistani personalities and places described by yes/no attributes. |
| **Actuators** | Streamlit interface that displays each question, the top candidate guesses with their probabilities, and the final guess. |
| **Sensors** | The player’s answers (Yes / Probably / Don’t know / Probably not / No), entered through buttons. |

## **3.2  Environment and Agent Type**

| Property | Classification — tick one |
| :---- | :---- |
| Observability | Fully observable  ☐          Partially observable  ☒ |
| Determinism | Deterministic  ☐          Stochastic  ☒ |
| Change over time | Static  ☒          Dynamic  ☐ |
| State and actions | Discrete  ☒          Continuous  ☐ |
| Agents | Single-agent  ☒          Multi-agent / adversarial  ☐ |
| Agent type | Simple reflex  ☐    Model-based  ☐    Goal-based  ☐    Utility-based  ☒    Learning  ☐ |

## **3.3  Problem Representation**

| Element | Your representation |
| :---- | :---- |
| **State representation** | A probability distribution over all N candidates, plus the questions asked so far and the answers received. |
| **Actions/moves** | Ask one unused attribute question, or make a final guess. |
| **Initial state** | Uniform prior over all candidates (each 1/N) with no questions asked. |
| **Goal or terminal test** | Top candidate’s probability reaches 0.85, and the player confirms the guess, or 20 questions have been asked. |
| **Cost, utility, fitness or evaluation** | Each question costs 1\. Candidate questions are scored by expected information gain, i.e. the expected drop in entropy of the distribution. |

# **4\.  Proposed AI Approach**

| \# | Technique | Role in the project | Own code or library |
| :---: | :---- | :---- | :---- |
| 1 | Bayesian belief updating with soft likelihoods | Updates every candidate’s probability after each answer and tolerates “probably” and wrong answers. | Own code |
| 2 | Information-gain (entropy) question selection | Chooses the unused question that most reduces uncertainty about the secret. | Own code |
| 3 | Pandas / NumPy data handling and Streamlit UI | Loads and filters the knowledge base and runs the game interface. | Library |
| B | Baseline: random question selection | Asks random unused questions with the same Bayesian update; used to measure what technique 2 adds. | Own code |

| The problem in Section 3 is partially observable and stochastic, so a probability distribution over candidates is the natural way to store what the agent knows. Bayes’ rule updates it after each answer. To cope with unreliable answers, we use soft likelihoods: a “Yes” multiplies a matching candidate by about 0.9 and a non-matching one by 0.1, while “Probably” uses gentler values such as 0.7 and 0.3. Because the agent is utility-based, it simulates each possible answer to every unused question, measures the entropy of the resulting distribution, and asks the question with the highest expected information gain, meaning the one that splits the remaining probability most evenly. We compare this against a baseline that picks random questions, which shows how much the heuristic actually contributes. |
| :---- |

## **4.1  Planned Class Design**

| Candidate: name, kind (person/place), attributes (dict) KnowledgeBase: load\_csv(), candidates, attribute\_matrix(), questions() BeliefState: probabilities, update(question, answer), entropy(), top\_k() QuestionSelector (abstract): select(belief, kb, asked) → question     InfoGainSelector(QuestionSelector): expected\_information\_gain()     RandomSelector(QuestionSelector): seeded random choice (baseline) GameAgent: has a BeliefState and a QuestionSelector; ask(), receive\_answer(), guess(), is\_done() SimulatedPlayer: secret, noise\_rate, rng; answer(question) Evaluator: uses GameAgent and SimulatedPlayer; run\_experiments(), compute\_metrics(), plot\_charts() app.py: Streamlit UI that wraps GameAgent |
| :---- |

# **5\.  Scope**

**In scope — the features you commit to delivering.** List the features that must work for the project to be considered complete.

| \# | Feature | Why it is essential |
| :---: | :---- | :---- |
| 1 | Knowledge base of about 150–200 personalities and places with about 40 yes/no attributes | The agent has nothing to reason over without it. |
| 2 | Bayesian update supporting five answer options | This is the core AI technique and handles uncertain answers. |
| 3 | Information-gain question selection | It makes the agent intelligent rather than a fixed script. |
| 4 | Streamlit game interface showing the current top guesses | It lets a real user play the game. |
| 5 | Automated evaluation against the random baseline using a simulated player | It provides evidence that the AI works. |
| 6 | Ability to add new characters when the AI guesses incorrectly. | It allows the knowledge base to grow and improves the game’s ability to identify new characters in future rounds.  |

**Out of scope — deliberately excluded.** Naming what you will not build is as important as naming what you will; it shows that your scope is realistic for a group of two.

| Free-text or voice input, learning new characters from players during play, a live web scraper, multiplayer or leaderboard features, mobile app packaging, and Urdu-language support. |
| :---- |

# **6\.  Data or Environment Source**

| Source name and URL | Hand-curated knowledge\_base.csv, compiled from public facts (e.g. Wikipedia and Wikidata, https\://www\.wikidata.org) and stored in the repository. |
| :---- | :---- |
| **Type** | Public dataset  ☐     Web API  ☐     Self-collected  ☒     Generated / simulated  ☐ |
| **Access requirements** | No key needed  ☒     Free key required  ☐     (Paid sources are not permitted) |
| **Approximate size** | About 150–200 rows × 40 attribute columns (under 1 MB). |
| **Licence/terms of use** | Our own compilation of factual data. Wikidata facts are CC0, and no Wikipedia text is copied. |
| **Offline fallback** | The CSV lives in the repository and is loaded locally, so no network is needed at runtime. Any data fetched while building it is saved to a local cache and read from there when offline. |

# **7\.  Evaluation Plan**

| What will be compared | Information-gain question selection versus the random-question baseline (optionally also a fixed-order question list). |
| :---- | :---- |
| **Metric(s)** | Success rate within 20 questions, average questions to a correct guess, and run time per game. |
| **Baseline** | Random question selection using the same Bayesian update. |
| **Test instances/test set** | Every candidate in the knowledge base used as the secret by a simulated player, at 0%, 5%, and 10% answer noise. |
| **Number of runs and seed** | 10 runs per candidate per noise level, fixed seed 42 for every approach. |
| **Planned charts (at least three)** | (1) Success rate by approach and noise level; (2) average questions to guess versus noise; (3) distribution of questions needed; (4) entropy versus question number. |

# **8\.  Division of Work**

| Member | Modules/components owned | Approximate share |
| :---- | :---- | :---: |
| Amnn Jindani | Knowledge base, Belief State and Bayesian update, report | 50% |
| Farwa Batool Naqvi | Question selectors, Streamlit UI, SimulatedPlayer, Evaluator and charts | 50% |

# **9\.  Milestones and Timeline**

| \# | Milestone — what will be demonstrably working | Target date | Owner |
| :---: | :---- | :---- | :---- |
| 1 | Knowledge base of 100+ entries loads in Pandas and a console game runs with random questions | 30 Oct 2026 | Amnn |
| 2 | Bayesian update works: the console game narrows candidates and prints the top 5 with probabilities | 6 Nov 2026 | Amnn |
| 3 | Information-gain selector beats the random baseline on 20 test secrets | 13 Nov 2026 | Farwa |
| 4 | Streamlit app is playable end to end, with noise handling and the simulated-player evaluator | 27 Nov 2026 | Farwa |
| 5 | Experiments complete, final integration, documentation and repository cleanup | 4 Dec 2026 | Both  |

# **10\.  Expected Outcome and Risks**

| When run, the Streamlit app asks the player to think of a Pakistani personality or place, then asks questions one at a time while showing a live list of the most likely candidates. We expect it to identify the secret in roughly 10–12 questions on average, compared with about 17 or more for random questions, and to keep a high success rate with 5–10% wrong answers. Our report will present the charts from Section 7\. Risk 1: the knowledge base may be too small or have uneven attributes, so some questions split candidates poorly. We would add attributes and candidates and drop questions with near-zero information gain. Risk 2: “probably” and wrong answers may confuse the model. We would tune the likelihood values and ask a confirming question before making a final guess. |
| :---- |

| For office use — Lab Instructor |  |
| :---- | :---- |
| Proposal status | Approved  ☐          Approved with changes  ☐          Revision required  ☐ |
| Comments |  |
| Signature and date |  |

*End of Project Proposal*

[image1]: <data:image/png;base64,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>