import numpy as np
from lp_solver import LPSolver
from world import generate_world_matrix, generate_payoff_matrix

class SimuManager:
    def __init__(self, rows=4, cols=4):
        self.rows = rows
        self.cols = cols
        self.world = None
        self.payoff_matrix = None
        self.human_role = None
        self.computer_role = None
        self.human_score = 0
        self.computer_score = 0
        self.current_round = 0

        self.actual_counts_hider = [0] * (rows * cols)
        self.actual_counts_seeker = [0] * (rows * cols)

        self.hider_strategy = None
        self.seeker_strategy = None

        self.game_history = []

        self.hider_index = None
        self.seeker_index = None

    def start_new_game(self, human_role=None):
        """Initialize world, payoff matrix, and assign roles."""
        self.reset_state()
        self.world = generate_world_matrix(self.rows, self.cols)
        self.payoff_matrix = generate_payoff_matrix(self.world)

        # If no human role is provided, simulate computer vs computer
        self.human_role = human_role
        self.computer_role = "seeker" if human_role == "hider" else "hider"

        self.set_computer_strategies()
        print("Game started. Hider and Seeker LP strategies computed.\n", self.payoff_matrix)

    def set_computer_strategies(self):
        hider_solver = LPSolver(self.payoff_matrix, role="hider")
        hider_solver.solve()
        self.hider_strategy = hider_solver.get_strategy_probabilities()

        seeker_solver = LPSolver(self.payoff_matrix, role="seeker")
        seeker_solver.solve()
        self.seeker_strategy = seeker_solver.get_strategy_probabilities()
        print("Hider strategy probabilities:", self.hider_strategy)
        print("Seeker strategy probabilities:", self.seeker_strategy)

    def start_round(self, human_row=None, human_col=None):
        self.current_round += 1

        # Computer vs Computer mode
        self.hider_index = self._computer_move(role="hider")
        self.seeker_index = self._computer_move(role="seeker")

        if self.seeker_index is not None:
            self._complete_round()

    def finish_round(self, human_row, human_col):
        if self.human_role != "seeker":
            raise RuntimeError("Only call finish_round when human is seeker.")

        self.seeker_index = human_row * self.cols + human_col
        self._complete_round()

    def _complete_round(self):
        score = self.payoff_matrix[self.hider_index][self.seeker_index]

        # computer vs computer
        self.human_score += score  # hider_score
        self.computer_score += (0 - score)  # seeker_score (since it's zero-sum)

        self.game_history.append({
            "round": self.current_round,
            "hider": self.hider_index,
            "seeker": self.seeker_index,
            "score": score,
            "result": "Seeker found the hider!" if self.hider_index == self.seeker_index else "Hider escaped!"
        })

    def _computer_move(self, role):
        strategy = self.hider_strategy if role == "hider" else self.seeker_strategy
        counts = self.actual_counts_hider if role == "hider" else self.actual_counts_seeker

        expected_counts = [p * self.current_round for p in strategy]
        differences = [e - a for e, a in zip(expected_counts, counts)]
        chosen_index = differences.index(max(differences))
        counts[chosen_index] += 1
        return chosen_index

    def reset_state(self):
        self.human_score = 0
        self.computer_score = 0
        self.current_round = 0
        self.game_history = []
        self.actual_counts_hider = [0] * (self.rows * self.cols)
        self.actual_counts_seeker = [0] * (self.rows * self.cols)
        self.hider_index = None
        self.seeker_index = None
