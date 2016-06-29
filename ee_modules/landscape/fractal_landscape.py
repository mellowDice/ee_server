import numpy as np
from math import sin, cos, pi, sqrt, ceil, floor, log

def build_landscape(width, height, octaves=8, scaling=1.8, seed=-1):
    landscape = np.zeros((width, height))

    # octaves limited if grid is too small
    octaves = min(floor(log(min(width, height), scaling))-1, octaves)
    scale = min(width, height)  # scale = size of features
    amplitude = 1
    for octave in range(octaves):
        # octave_intensity = noise_2d(width, height, width, height, seed=seed) * amplitude
        amplitude *= noise_2d(width, height, width/2, height/2, seed=seed)
        landscape = landscape * (1 - amplitude) + noise_2d(width, height, scale, scale, seed=seed) * amplitude
        scale /= scaling
    print('in build_landscape')
    return landscape
                  
def noise_2d(width, height, period_width, period_height, seed=-1):
    # ensure everything is an integer
    width //= 1
    height //=1
    period_width //=1
    period_height //=1

    # set the seed if one is set
    if seed != -1:
        np.random.seed(seed)

    coarse_i_count = ceil(width / period_width)
    coarse_j_count = ceil(height / period_height)

    # The 2D course-grid matrix of random unit vectors, which defines the grid, with submatrix [[upper-left, upper-right], [bottom-left, bottom-right]], with subarray [vector-x, vector-y]
    coarse_grid = np.random.rand(coarse_i_count + 1, coarse_j_count + 1) * 2 * pi
    coarse_grid = np.array([[coarse_grid[:-1, :-1], coarse_grid[1:, :-1]],
                            [coarse_grid[:-1, 1: ], coarse_grid[1:, 1: ]]])
    coarse_grid = np.array([np.cos(coarse_grid), np.sin(coarse_grid)]).transpose(3, 4, 2, 1, 0)
    # generate fine grid by repeating coarse grid to fill space
    fine_coarse_grid = np.repeat(np.repeat(coarse_grid, period_width, axis=0), period_height, axis=1)

    # create a left-to-right gradient in fine grid dimensions
    h_step = 1/period_width
    v_step = 1/period_height
    fine_grid_gradient_up, fine_grid_gradient_left = np.mgrid[1-h_step/2 : 0 : -h_step, 1-v_step/2 : 0 : -v_step]

    # The 2D fine-grid weighting matrix for interpolation, with submatrix [[upper-left, upper-right], [bottom-left, bottom-right]], and vector subarray [vector-x, vector-y] (vector-x = vector-y)
    weighting_fine_grid = fine_grid_gradient_left * fine_grid_gradient_up
    weighting_fine_grid = np.array([
                                    [
                                     [weighting_fine_grid[:   , :], weighting_fine_grid[:   , ::-1]],  # upper-left and upper-right weightings
                                     [weighting_fine_grid[::-1, :], weighting_fine_grid[::-1, ::-1]]   # lower-left and lower-right weightings
                                    ],] * 2
                                   ).transpose(3, 4, 1, 2, 0)
    weighting_fine_grid = 3*weighting_fine_grid**2 - 2*weighting_fine_grid**3
    weighting_fine_grid_tiled = np.tile(weighting_fine_grid, (coarse_i_count, coarse_j_count, 1, 1, 1))

    # The 2D fine-grid vectors matrix for determining height (by multiplying vs. coarse-grid vectors), with submatrix [[upper-left, upper-right], [bottom-left, bottom-right]], and vector subarray [vector-x, vector-y]
    vectors_fine_grid = np.array( 
                            [[[-fine_grid_gradient_left[:, ::-1], -fine_grid_gradient_up[::-1, :]],   # upper-left
                              [ fine_grid_gradient_left[:, :   ], -fine_grid_gradient_up[::-1, :]]],  # upper-right
                             [[-fine_grid_gradient_left[:, ::-1],  fine_grid_gradient_up[:   , :]],   # lower-left
                              [ fine_grid_gradient_left[:, :   ],  fine_grid_gradient_up[:   , :]]]]  # lower-right
                        ).transpose(3, 4, 0, 1, 2)
    vectors_fine_grid_tiled = np.tile(vectors_fine_grid, (coarse_i_count, coarse_j_count, 1, 1, 1))
    fine_grid = fine_coarse_grid * vectors_fine_grid_tiled * weighting_fine_grid_tiled

    # add multiplied vector-x + multiplied vector-y to get dot product
    fine_grid = fine_grid.transpose(4, 0, 1, 2, 3)
    fine_grid = fine_grid[0] + fine_grid[1]

    fine_grid = fine_grid.transpose(2, 3, 0, 1)
    fine_grid = fine_grid[0,0] + fine_grid[1,0] + fine_grid[0,1] + fine_grid[1,1] 

    return fine_grid[:width, :height] + 0.5


# landscape = noise_2d(200,200,100,100)
# landscape = build_landscape(200, 200, octaves=8)
# np.savetxt('test.txt', landscape)