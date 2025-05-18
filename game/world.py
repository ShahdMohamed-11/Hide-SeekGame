import random
import numpy as np

def generate_world_matrix(rows=4, cols=4):
     return [[3,3,3,2],[1,2,2,3],[2,1,2,3],[2,3,2,2]]

def manhattan_distance(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)

def generate_payoff_matrix(world):
    print("Generating payoff matrix...")
    rows, cols = len(world), len(world[0])
    size = rows * cols
    
    # Initialize payoff matrix with zeros
    matrix = [[0 for _ in range(size)] for _ in range(size)]
    
    # For each hider position
    for h_row in range(rows):
        for h_col in range(cols):
            h_index = h_row * cols + h_col
            place_type = world[h_row][h_col]
            
            for s_row in range(rows):
                for s_col in range(cols):
                    s_index = s_row * cols + s_col
                    distance = manhattan_distance(h_row, h_col, s_row, s_col)

                    # Base score
                    if h_row == s_row and h_col == s_col:
                        # Seeker finds hider
                        score = -1 if place_type in [1, 2] else -3
                    else:
                        # Seeker does not find hider
                        score = 1 if place_type in [2, 3] else 2

                        # Apply penalty if seeker is near hider
                        if distance == 1:
                            score *= 0.5
                        elif distance == 2:
                            score *= 0.75
                        # Else multiplier is 1 (no need to change)

                    matrix[h_index][s_index] = round(score, 2)

    # # Print the matrix
    # print("Payoff Matrix:")
    # for row in matrix:
    #     print(row)

    return matrix