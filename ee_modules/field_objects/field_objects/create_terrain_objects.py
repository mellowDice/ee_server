import numpy as np

obstacles = {}
food = {}
height = 100
width = 100
terrain = {}

# Factor this out with redis and replace with references 
def save_terrain(height, width, terrain):
  global terrain, width, height
  terrain = terrain
  height = height
  width = width
  print('vars set: ', height, width, terrain)]

def random_coordinates():
  global terrain, height
  coordinates = np.random.randint(height, size=2).tolist()
  x = coordinates[0]
  y = coordinates[1]
  z = terrain[x][y]
  print('coordinate', x, y, z)
  return {'x': x, 'y': y, 'z': z}

def create_terrain_object(type, id) {
  global food, obstacles
  if type == 'food':
    food[id] = update_terrain_object[id]
  else:
    obstacles[id] = update_terrain_object[id]
}

def update_terrain_object(idNum):
  data = random_coordinates()
  data.id = idNum
  return data

# New players can access all terrain
def get_all_food():
  global food
  return food

def get_all_obstacles():
  global obstacles
  return obstacles


# ??import time, threading