import numpy as np
from math import sin, cos, pi, sqrt

def create_landscape(width, height, period_width, period_height):
    np.random.seed(0)
    coarse_i_count = width // period_width
    coarse_j_count = height // period_height

    # The 2D course-grid matrix of random unit vectors, which defines the grid, with submatrix [[upper-left, upper-right], [bottom-left, bottom-right]], with subarray [vector-x, vector-y]
    coarse_grid = np.random.rand(coarse_i_count + 1, coarse_j_count + 1) * 2 * pi
    coarse_grid = np.array([[coarse_grid[:-1,:-1], coarse_grid[1:,:-1]], [coarse_grid[:-1,1:], coarse_grid[1:,1:]]])
    coarse_grid = np.array([np.cos(coarse_grid), np.sin(coarse_grid)]).transpose(3, 4, 1, 2, 0)
    fine_coarse_grid = np.repeat(np.repeat(coarse_grid, period_width, axis=0), period_height, axis=1)
    # generate fine grid by repeating coarse grid to fill space
    # fine_grid_vectors_4corners = np.repeat(np.repeat(coarse_grid_vectors_4corners, period_width, axis=0), period_height, axis=1)

    # create a left-to-right gradient in fine grid dimensions
    fine_grid_gradient_left = np.array([np.linspace(1, 0, period_width+1),] * (period_height+1))
    fine_grid_gradient_up = fine_grid_gradient_left.transpose()
    
    # The 2D fine-grid weighting matrix for interpolation, with submatrix [[upper-left, upper-right], [bottom-left, bottom-right]], and vector subarray [vector-x, vector-y] (vector-x = vector-y)
    weighting_fine_grid = fine_grid_gradient_left * fine_grid_gradient_up
    weighting_fine_grid = np.array([
                                    [
                                     [weighting_fine_grid[:-1  , :-1], weighting_fine_grid[:-1  , :0:-1]],  # upper-left and upper-right weightings
                                     [weighting_fine_grid[:0:-1, :-1], weighting_fine_grid[:0:-1, :0:-1]]   # lower-left and lower-right weightings
                                    ],] * 2
                                   ).transpose(3, 4, 1, 2, 0)
    weighting_fine_grid = 3*weighting_fine_grid**2 - 2*weighting_fine_grid**3
    weighting_fine_grid_tiled = np.tile(weighting_fine_grid, (coarse_i_count, coarse_j_count, 1, 1, 1))
    # weighting_fine_grid = np.tile(weighting_fine_grid, (coarse_i_count, coarse_j_count))

    # The 2D fine-grid vectors matrix for determining height (by multiplying vs. coarse-grid vectors), with submatrix [[upper-left, upper-right], [bottom-left, bottom-right]], and vector subarray [vector-x, vector-y]
    vectors_fine_grid = np.array( 
                            [[[fine_grid_gradient_left[:-1, :0:-1], fine_grid_gradient_up[:0:-1, :-1]],   # upper-left
                              [fine_grid_gradient_left[:-1, :-1]  , fine_grid_gradient_up[:0:-1, :-1]]],  # upper-right
                             [[fine_grid_gradient_left[:-1, :0:-1], fine_grid_gradient_up[:-1  , :-1]],   # lower-left
                              [fine_grid_gradient_left[:-1, :-1]  , fine_grid_gradient_up[:-1  , :-1]]]]  # lower-right
                        ).transpose(3, 4, 0, 1, 2)
    vectors_fine_grid_tiled = np.tile(vectors_fine_grid, (coarse_i_count, coarse_j_count, 1, 1, 1))
    fine_grid = fine_coarse_grid * vectors_fine_grid_tiled * weighting_fine_grid_tiled

    # add multiplied vector-x + multiplied vector-y to get dot product
    fine_grid = fine_grid.transpose(4, 0, 1, 2, 3)
    fine_grid = fine_grid[0] + fine_grid[1]

    fine_grid = fine_grid.transpose(2, 3, 0, 1)
    fine_grid = fine_grid[0,0] + fine_grid[1,0] + fine_grid[0,1] + fine_grid[1,1] 

    return fine_grid / sqrt(2) * 2


landscape = create_landscape(200, 200, 100, 100)
np.savetxt('test.txt', landscape)