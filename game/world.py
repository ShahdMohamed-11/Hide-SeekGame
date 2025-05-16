import random
import numpy as np

def generate_world_matrix(rows=4, cols=4):
    return [[random.choice([1, 2, 3]) for _ in range(cols)] for _ in range(rows)]

def generate_payoff_matrix(world):

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
    
    return matrix

def position_to_notation(index, cols):
    """Convert a 1D index to (row, col) notation"""
    row = index // cols
    col = index % cols
    return f"({row},{col})"

# Example usage:
rows, cols = 4, 4
world = generate_world_matrix(rows, cols)
payoff_matrix = generate_payoff_matrix(world)

print("World matrix (1=Neutral, 2=Easy, 3=Hard):")
for row in world:
    print(row)


# Print column headers (seeker positions)
print( end="\t")
for s in range(rows * cols):
    print(position_to_notation(s, cols), end="\t")
print()

# Print payoff matrix with row headers (hider positions)
for h in range(rows * cols):
    print(position_to_notation(h, cols), end="\t")
    for s in range(rows * cols):
        print(payoff_matrix[h][s], end="\t")
    print()

print("\nExample analysis:")