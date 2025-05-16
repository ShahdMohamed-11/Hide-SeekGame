

# def next_position(probabilities):
#     global round, actual_counts
#     round += 1

#     expected_counts = [p * round for p in probabilities]
#     differences = [e - a for e, a in zip(expected_counts, actual_counts)]

#     # Pick the index with the max positive difference (most underused)
#     index = differences.index(max(differences))
#     actual_counts[index] += 1
#     return index
# round = 0
# actual_counts = [0] * 16


# import random

# # Initialize round number and count tracker
# round_number = 0
# actual_counts = [0] * 3

# # Generate a random probability distribution of length 16
# probabilities = [0,2/3,1/3]
# total = sum(probabilities)
# probabilities = [p / total for p in probabilities]

# # Store history of counts after each round
# round_history = []

# def next_position(probabilities):
#     global round_number, actual_counts
#     round_number += 1

#     # Calculate expected counts up to this round
#     expected_counts = [p * round_number for p in probabilities]
#     differences = [e - a for e, a in zip(expected_counts, actual_counts)]

#     # Choose the most under-picked position
#     index = differences.index(max(differences))
#     actual_counts[index] += 1


#     return index

# # Run for 10 rounds
# for _ in range(11):
#     next_position(probabilities)


# # Print final results
# print("Final actual counts:", actual_counts)
# print("Used probabilities:", [round(p, 4) for p in probabilities])


# Placeholder for game_manager.py

import numpy as np
from lp_solver import LPSolver
from world import generate_world_matrix, generate_payoff_matrix

class GameManager:
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
        self.actual_counts = [0] * 16
        self.computer_strategy = None  #probabilities of places for computer
        self.game_history = []

    def start_new_game(self, human_role):
        """Initialize world, payoff matrix, and assign roles."""
        self.reset_state()
        self.world = generate_world_matrix(self.rows, self.cols)
        self.payoff_matrix = generate_payoff_matrix(self.world)
        self.human_role = human_role
        self.computer_role = "seeker" if human_role == "hider" else "hider"
        self.set_computer_strategy()
        
       
    def set_computer_strategy(self):
        solver = LPSolver(self.payoff_matrix, role=self.computer_role)
        solver.solve()
        self.computer_strategy = solver.get_strategy_probabilities()
    
  
    def start_round(self, human_row=None, human_col=None):
        self.current_round += 1
 
        if self.human_role == "hider":
          if human_row is None or human_col is None:
            raise ValueError("Hider must provide position at start of round.")
          self.hider_index = human_row * self.cols + human_col
          self.seeker_index = self.computer_move()
          self._complete_round()
        else:
          self.hider_index = self.computer_move()
          self.seeker_index = None  # wait for human seeker move later

    def finish_round(self, human_row, human_col):
    
      if self.human_role != "seeker":
        raise RuntimeError("Only call finish_round when human is the seeker.")

      self.seeker_index = human_row * self.cols + human_col
      self._complete_round()
    
    def _complete_round(self):
     score = self.payoff_matrix[self.hider_index][self.seeker_index]

     if self.human_role == "hider":
        self.human_score += score
        self.computer_score -= score
     else:
        self.human_score -= score
        self.computer_score += score

     self.game_history.append({
        "round": self.current_round,
        "human_role": self.human_role,
        "computer_role": self.computer_role,
        "hider": self.hider_index,
        "seeker": self.seeker_index,
        "score": score,
        "result": "Seeker found the hider!" if self.hider_index == self.seeker_index else "Hider escaped!"
    })

  
    def computer_move(self):
        """Computer chooses its position based on LP and frequency-based selection."""
        expected_counts = [p * self.current_round for p in self.computer_strategy]
        differences = [e - a for e, a in zip(expected_counts, self.actual_counts)]
        computer_index = differences.index(max(differences))
        
        self.actual_counts[computer_index] += 1  
        return computer_index
    

    def reset_state(self):
        """Reset game state for a new session."""
        self.human_score = 0
        self.computer_score = 0
        self.current_round = 0
        self.game_history = []
        self.actual_counts = [0] * (self.rows * self.cols)


  

  
# --------------------
# Example usage:
# --------------------
if __name__ == "__main__":
    game = GameManager(rows=4, cols=4, num_rounds=10)

    game.start_new_game(player_role="hider")

    # Simulate 10 moves from player as (row, col)
    moves = [(0, 0), (1, 1), (2, 2), (3, 0), (0, 3), (1, 2), (2, 1), (3, 3), (0, 1), (1, 0)]
    for move in moves:
        try:
            result, score = game.play_round(move)
            print(f"Round {game.current_round}: {result} | Round Score: {score}")
        except Exception as e:
            print(e)
            break

    # Final stats
    print("\nGame Summary:")
    for k, v in game.get_summary().items():
        print(f"{k}: {v}")