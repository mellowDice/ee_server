import numpy as np
from math import sin, cos, pi

def create_landscape(width, height, period_width, period_height):
    np.random.seed(0)
    coarse_i_count = width // period_width + 1
    coarse_j_count = height // period_height + 1

    # coarse grid consists of 2D matrix, with submatrix [[upper-left, upper-right], [bottom-left, bottom-right]], with subarray [vector-x, vector-y] of random unit vectors
    coarse_grid_angles = np.random.rand(coarse_i_count, coarse_j_count)
    coarse_grid_vectors = np.array([np.cos(coarse_grid_angles), np.sin(coarse_grid_angles)]).transpose(1, 2, 0)
    coarse_grid_vectors_4corners = np.array([[coarse_grid_vectors,] * 2,] * 2).transpose(3, 4, 0, 1, 2)

    # generate fine grid by repeating coarse grid to fill space
    fine_grid_vectors_4corners = np.repeat(np.repeat(coarse_grid_vectors_4corners, period_width, axis=0), period_height, axis=1)

    # create a left-to-right gradient in fine grid dimensions
    fine_grid_template = np.array([np.linspace(1, 0, period_width+1),] * (period_height+1))
    print(fine_grid_template)
    
    # The 2D fine-grid weighting matrix, with submatrix [[upper-left, upper-right], [bottom-left, bottom-right]], and subarray [vector-x, vector-y] (vector-x = vector-y)
    weighting_fine_grid = fine_grid_template * fine_grid_template.transpose()
    weighting_fine_grid = np.array([[[weighting_fine_grid[:-1,:-1], weighting_fine_grid[:-1,::-1][:,:-1]],
                                     [weighting_fine_grid[::-1,:-1][:-1,:], weighting_fine_grid[::-1,::-1][:-1,:-1]]],] * 2).transpose(3, 4, 1, 2, 0)
    weighting_fine_grid = np.tile(weighting_fine_grid, (coarse_i_count, coarse_j_count))

    vectors_fine_grid = np.array([fine_grid_template, fine_grid_template]).transpose(1, 2, 0)
    print(vectors_fine_grid)



    # print(fine_grid_weighting)


    # fine_grid_weighting_template = fine_grid_weighting_template[:-1,::-1]

    # return fine_grid_weighting_template
    # return coarse_grid;
    # fine_grid_angles = np.repeat(np.repeat(a, period_height, axis=0), period_width, axis=1)


print(create_landscape(1000, 1000, 10, 10))