import numpy as np

obstacles = {}
food = {}
height = 100
width = 100
terrain = {}

# Factor this out with redis and replace with references 
def save_terrain(rows, columns, landscape):
  global terrain, width, height
  terrain = landscape
  height = rows
  width = columns

def random_coordinates():
  global terrain, height
  print('terrain exists before random coordinates called', terrain)
  coordinates = np.random.randint(height, size=2).tolist()
  x = coordinates[0]
  y = coordinates[1]
  z = terrain[coordinates[0]][coordinates[1]]
  return {'x': x, 'y': y, 'z': z}

def create_or_update_terrain_object(type, id):
  global food, obstacles
  coordinates = random_coordinates(id)
  if type == 'food':
    food[id] = coordinates
  else:
    obstacles[id] = coordinates
  return coordinates

# New players can access all terrain
def get_all_food():
  global food
  print(food)
  if len(food) == 0:
      for i in range(100):
        create_or_update_terrain_object('food', i)
  return food

def get_all_obstacles():
  global obstacles
  print(obstacles)
  if len(obstacles) == 0:
    for j in range(15):
      create_or_update_terrain_object('obstacles', j)
  return obstacles


# ??import time, threading