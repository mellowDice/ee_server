import random
from math import sin, cos, pi
from functools import reduce
landscape_scale_factor = 20

def fractal_landscape(x_size, y_size, x_res, y_res, levels=1, dampening=0.4, seed=0):
    amplitude = 1
    result = new_2D_matrix(x_size, y_size)
    for level in range(levels):
        perlin = perlin_2D(x_size, y_size, x_res // 2**level, y_res // 2**level, seed)
        result = [[(result[x][y] + landscape_scale_factor * perlin[x][y]*amplitude) for y in range(y_size)] for x in range(x_size)]
        amplitude *= dampening
    return result

def perlin_2D(x_size, y_size, x_res, y_res, seed=0):
    fine_grid = new_2D_matrix(x_size, y_size)
    coarse_grid = create_coarse_grid(x_size // x_res + 1, y_size // y_res + 1, seed)
    for x in range(len(coarse_grid)-1):
        for y in range(len(coarse_grid[x])-1):
            a00 = coarse_grid[x][y]
            a01 = coarse_grid[x][y+1]
            a10 = coarse_grid[x+1][y]
            a11 = coarse_grid[x+1][y+1]
            local_fine_grid = create_local_fine_grid(x_res, y_res, a00, a01, a10, a11)
            for local_x in range(len(local_fine_grid)):
                for local_y in range(len(local_fine_grid[local_x])):
                    fine_grid[local_x + x * x_res][local_y + y * y_res] = local_fine_grid[local_x][local_y]
    return fine_grid


def create_local_fine_grid(x_res, y_res, a00, a10, a01, a11):
    fine_grid = new_2D_matrix(x_res, y_res)
    for j in range(y_res):
        for i in range(x_res):
            # what is the location of the subpoint?
            x = i / x_res
            y = j / y_res
            # what are the 4 dot products
            n00 = dot_product_2D((x  , y  ), a00)
            n01 = dot_product_2D((1-x, y  ), a01)
            n10 = dot_product_2D((x  , 1-y), a10)
            n11 = dot_product_2D((1-x, 1-y), a11)
            # linearly interpolate
            fine_grid[i][j] = smoothinterp(smoothinterp(n00, n01, x), smoothinterp(n10, n11, x), y)
    return fine_grid;


def create_coarse_grid(rows, cols, seed=0):
    """create grid with tuples representing random unit vectors"""
    random.seed(seed)
    return [[angle_to_unit_vector(random.uniform(0, 2*pi)) for j in range(cols)] for i in range(rows)]


def angle_to_unit_vector(angle):
    return cos(angle), sin(angle)


def lerp(a0, a1, w):
    return (1.0 - w)*a0 + w*a1


def cosinterp(a0, a1, w):
    return (a0-a1)*((cos(w * pi)+1)/2) + a1


def smoothinterp(a0, a1, w):
    return (a0-a1)*((3*(w-1)**2 + 2*(w-1)**3)) + a1


def dot_product_2D(m0, m1):
    return m0[0]*m1[0] + m0[1]*m1[1]


def new_2D_matrix(x, y):
    return [[0 for j in range(y)] for i in range(x)]


# fine_grid = fractal_landscape(x_size=300, y_size=300, x_res=300, y_res=300, levels=8, dampening=0.4)
# print(fine_grid)
# print('\n'.join([' '.join([str(20*cell*1000//1/1000) for cell in row]) for row in fine_grid]))