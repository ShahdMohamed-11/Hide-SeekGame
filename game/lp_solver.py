
import numpy as np
from scipy.optimize import linprog

class LPSolver:
   
    def __init__(self, payoff_matrix, role):
        self.payoff_matrix = np.array(payoff_matrix)
        self.role = role  #  hider or seeker
        self.strategy_probabilities = None
        self.value_of_game = None
    
    def solve(self):
        if self.role == "hider":
            self._solve_for_hider()
        elif self.role == "seeker":
            self._solve_for_seeker()
        else:
            raise ValueError("Role must be either 'hider' or 'seeker'")
        
        return self.strategy_probabilities, self.value_of_game
    
    def _solve_for_hider(self):
        num_rows, num_cols = self.payoff_matrix.shape
        # Objective: minimize v
        c = np.zeros(num_rows + 1)
        c[-1] = -1 
        A_ub = np.zeros((num_cols, num_rows + 1))
        for j in range(num_cols):
            A_ub[j, :-1] = -self.payoff_matrix[:, j]  
            A_ub[j, -1] = 1  
        
        b_ub = np.zeros(num_cols)
        
        # Equality constraint: sum(p_i) = 1
        A_eq = np.zeros((1, num_rows + 1))
        A_eq[0, :-1] = 1  # Coefficients for p_i
        b_eq = np.ones(1)
          
        bounds = [(0, None) for _ in range(num_rows)] + [(None, None)]  
        
        # Solve the LP problem
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if result.success:
            self.strategy_probabilities = result.x[:-1]  
            self.value_of_game = result.x[-1] 
        else:
            raise RuntimeError(f"LP solver failed: {result.message}")
    
    def _solve_for_seeker(self):
        num_rows, num_cols = self.payoff_matrix.shape
       
        c = np.zeros(num_cols + 1)
        c[-1] = 1 
       
        A_ub = np.zeros((num_rows, num_cols + 1))
        for i in range(num_rows):
            A_ub[i, :-1] = self.payoff_matrix[i, :]  
            A_ub[i, -1] = -1 
        
        b_ub = np.zeros(num_rows)
        
       
        A_eq = np.zeros((1, num_cols + 1))
        A_eq[0, :-1] = 1  
        b_eq = np.ones(1)
        
        
        bounds = [(0, None) for _ in range(num_cols)] + [(None, None)]  
        
        
        result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs')
        
        if result.success:
            self.strategy_probabilities = result.x[:-1]  
            self.value_of_game = result.x[-1]  
        else:
            raise RuntimeError(f"LP solver failed: {result.message}")
    
    def get_strategy_probabilities(self):
        return self.strategy_probabilities
    
    def get_value_of_game(self):
        return self.value_of_game

if __name__ == "__main__":
    # Example payoff matrix (hider's perspective)
    matrix = [
        [1, -1, 3],
        [3, 5, -3],
        [6, 2, -2]
    ]
    
    # Test as hider
    solver_hider = LPSolver(matrix, role="hider")
    solver_hider.solve()
    print("Hider's strategy probabilities:", solver_hider.get_strategy_probabilities())
    print("Value of game (hider):", solver_hider.get_value_of_game())
    
    # Test as seeker
    solver_seeker = LPSolver(matrix, role="seeker")
    solver_seeker.solve()
    print("Seeker's strategy probabilities:", solver_seeker.get_strategy_probabilities())
    print("Value of game (seeker):", solver_seeker.get_value_of_game())