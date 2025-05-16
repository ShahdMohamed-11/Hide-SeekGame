import random
import numpy as np

def generate_world_matrix(rows=4, cols=4):
    return [[random.choice([1, 2, 3]) for _ in range(cols)] for _ in range(rows)]

def generate_payoff_matrix(world):
    print("Generating payoff matrix...")
    rows, cols = len(world), len(world[0])
    size = rows * cols
    
    # Initialize payoff matrix with zeros
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    
    # For each hider position (h_row, h_col)
    for h_row in range(rows):
        for h_col in range(cols):
            h_index = h_row * cols + h_col  # Convert 2D position to 1D index
            place_type = world[h_row][h_col]
            
            # For each seeker position (s_row, s_col)
            for s_row in range(rows):
                for s_col in range(cols):
                    s_index = s_row * cols + s_col  # Convert 2D position to 1D index
                    
                    if h_row == s_row and h_col == s_col:
                        # Seeker finds hider
                        if place_type == 1 or place_type == 2:
                            score = -1
                        elif place_type == 3:
                            score = -3
                    else:
                        # Seeker does not find hider
                        if place_type == 1 or place_type == 3:
                            score = 1
                        elif place_type == 2:
                            score = 2
                    
                    matrix[h_index][s_index] = score

    # Print the matrix
    print("Payoff Matrix:")
    for row in matrix:
        print(row)
                    
    
    return matrix



