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
        print("Game started. ", self.human_role, self.computer_role)  
        self.set_computer_strategy()
         
    def set_computer_strategy(self):
        solver = LPSolver(self.payoff_matrix, role=self.computer_role)
        print("jananananm")  
        solver.solve()
        print("janananan")  
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



