
import time
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from game_agent import GameAgent
from question_selector import InfoGainSelector, RandomSelector
from simulated_player import SimulatedPlayer


class Evaluator:
    """Evaluates Information Gain against Random question selection."""

    def __init__(
        self,
        kb,
        noise_levels=(0.0, 0.05, 0.10),
        runs_per_candidate=10,
        max_questions=20,
        seed=42
    ):
        self.kb = kb
        self.noise_levels = noise_levels
        self.runs_per_candidate = runs_per_candidate
        self.max_questions = max_questions
        self.seed = seed

        self.results = []
        self.entropy_histories = []

        self.strategies = {
            "Information Gain": InfoGainSelector,
            "Random": RandomSelector
        }

    def run_game(self, candidate_index, noise_rate, strategy, run_seed):
        """Run one game using a selected strategy."""

        secret = self.kb.candidate(candidate_index)

        player_rng = np.random.default_rng(run_seed)

        player = SimulatedPlayer(
            secret=secret,
            noise_rate=noise_rate,
            rng=player_rng
        )

        if strategy == "Information Gain":
            selector = InfoGainSelector()
        else:
            selector = RandomSelector(seed=run_seed)

        agent = GameAgent(
            kb=self.kb,
            selector=selector,
            max_questions=self.max_questions
        )

        entropy_history = [agent.belief.entropy()]

        start_time = time.perf_counter()

        while not agent.is_done():

            question = agent.ask()

            if question is None:
                break

            answer = player.answer(question)

            agent.receive_answer(answer)

            entropy_history.append(agent.belief.entropy())

        runtime = time.perf_counter() - start_time

        guess = agent.guess()

        success = guess.name == secret.name

        return {
            "Candidate": secret.name,
            "Strategy": strategy,
            "Noise_Level": noise_rate,
            "Questions": len(agent.belief.asked),
            "Success": success,
            "Runtime": runtime,
            "Entropy_History": entropy_history
        }

    def run_experiments(self):
        """Run experiments for every candidate, noise level and strategy."""

        self.results = []
        self.entropy_histories = []

        for noise in self.noise_levels:

            for candidate_index in range(len(self.kb)):

                for run in range(self.runs_per_candidate):

                    run_seed = (
                        self.seed
                        + candidate_index * 1000
                        + run
                        + int(noise * 10000)
                    )

                    for strategy in self.strategies:

                        result = self.run_game(
                            candidate_index,
                            noise,
                            strategy,
                            run_seed
                        )

                        self.results.append({
                            key: value
                            for key, value in result.items()
                            if key != "Entropy_History"
                        })

                        self.entropy_histories.append({
                            "Strategy": strategy,
                            "Noise_Level": noise,
                            "History": result["Entropy_History"]
                        })

        self.results = pd.DataFrame(self.results)

        return self.results

    def compute_metrics(self):
        """Calculate evaluation metrics for each strategy and noise level."""

        if self.results is None or self.results.empty:
            raise ValueError("Run experiments before calculating metrics.")

        metrics = []

        grouped = self.results.groupby(
            ["Strategy", "Noise_Level"]
        )

        for (strategy, noise), group in grouped:

            successful_games = group[group["Success"]]

            success_rate = group["Success"].mean() * 100

            if not successful_games.empty:
                average_questions = successful_games["Questions"].mean()
            else:
                average_questions = np.nan

            average_runtime = group["Runtime"].mean()

            metrics.append({
                "Strategy": strategy,
                "Noise_Level": noise,
                "Success_Rate": success_rate,
                "Average_Questions_To_Correct_Guess": average_questions,
                "Average_Runtime": average_runtime
            })

        return pd.DataFrame(metrics)

    def plot_charts(self, output_dir="outputs"):
        """Generate and save the four evaluation charts."""

        if self.results is None or self.results.empty:
            raise ValueError("Run experiments before plotting charts.")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        metrics = self.compute_metrics()

        # Chart 1: Success rate by strategy and noise level
        success_pivot = metrics.pivot(
            index="Noise_Level",
            columns="Strategy",
            values="Success_Rate"
        )

        ax = success_pivot.plot(
            kind="bar",
            figsize=(9, 5)
        )

        ax.set_title("Success Rate by Strategy and Noise Level")
        ax.set_xlabel("Noise Level")
        ax.set_ylabel("Success Rate (%)")
        ax.set_xticklabels(
            [f"{x * 100:.0f}%" for x in success_pivot.index],
            rotation=0
        )
        ax.legend(title="Strategy")
        plt.tight_layout()
        plt.savefig(output_path / "success_rate.png")
        plt.close()

        # Chart 2: Average questions needed for correct guesses
        questions_pivot = metrics.pivot(
            index="Noise_Level",
            columns="Strategy",
            values="Average_Questions_To_Correct_Guess"
        )

        ax = questions_pivot.plot(
            kind="line",
            marker="o",
            figsize=(9, 5)
        )

        ax.set_title("Average Questions Needed for Correct Guesses")
        ax.set_xlabel("Noise Level")
        ax.set_ylabel("Average Questions")
        ax.set_xticks(list(questions_pivot.index))
        ax.set_xticklabels(
            [f"{x * 100:.0f}%" for x in questions_pivot.index]
        )
        ax.legend(title="Strategy")
        plt.tight_layout()
        plt.savefig(output_path / "average_questions.png")
        plt.close()

        # Chart 3: Distribution of questions needed
        plt.figure(figsize=(9, 5))

        for strategy in self.strategies:

            data = self.results[
                self.results["Strategy"] == strategy
            ]

            plt.hist(
                data["Questions"],
                bins=range(1, self.max_questions + 2),
                alpha=0.5,
                label=strategy
            )

        plt.title("Distribution of Questions Needed")
        plt.xlabel("Number of Questions")
        plt.ylabel("Number of Games")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path / "question_distribution.png")
        plt.close()

        # Chart 4: Average entropy vs question number
        plt.figure(figsize=(10, 6))

        for strategy in self.strategies:

            for noise in self.noise_levels:

                histories = [
                    item["History"]
                    for item in self.entropy_histories
                    if item["Strategy"] == strategy
                    and item["Noise_Level"] == noise
                ]

                if not histories:
                    continue

                average_entropy = []

                for question_number in range(self.max_questions + 1):

                    values = [
                        history[question_number]
                        for history in histories
                        if len(history) > question_number
                    ]

                    if values:
                        average_entropy.append(np.mean(values))
                    else:
                        break

                plt.plot(
                    range(len(average_entropy)),
                    average_entropy,
                    marker="o",
                    label=f"{strategy}, {noise * 100:.0f}% noise"
                )

        plt.title("Average Entropy vs Number of Questions")
        plt.xlabel("Number of Questions")
        plt.ylabel("Entropy (bits)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_path / "entropy_progression.png")
        plt.close()

        return output_path

    def save_results(self, output_dir="outputs"):
        """Save experiment results and evaluation metrics."""

        if self.results is None or self.results.empty:
            raise ValueError("Run experiments before saving results.")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        metrics = self.compute_metrics()

        self.results.to_csv(
            output_path / "experiment_results.csv",
            index=False
        )

        metrics.to_csv(
            output_path / "evaluation_metrics.csv",
            index=False
        )

        return metrics
