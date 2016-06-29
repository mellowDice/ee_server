import eventlet
eventlet.monkey_patch()

from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit, join_room
from ee_modules.landscape.fractal_landscape import build_landscape

import datetime
import json
import numpy as np
import requests
import erequests
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

microservices_urls = {
    'terrain': 'http://localhost:5000'
}

socketio = SocketIO(app, async_mode='eventlet')

all_users = []
user_count = 0
food = {}
obstacles = {}
terrain = {}

@app.route('/')
def index():
    return 'Welcome to Ethereal Epoch'

@app.route('/send_terrain', methods=['POST'])
def terrain_creator():
    global terrain
    # terrain = data.terrain
    socketio.emit('terrain', {'terrain': request.json["terrain"]}, broadcast=True)
    return 'Ok'


# @app.route('/get_terrain_data')
# def terrain(data):
    
# Helper Functions

def create_location_object(user_id, data):
    x = data["x"]
    y = data["y"]
    z = data["z"]
    return {'id': user_id, 'x': x, 'y': y, 'z': z}

def get_random_coordinate(height):
    global terrain
    coordinates = np.random.randint(height, size=2).tolist()
    position = {'x': coordinates[0], 'y': coordinates[1], 'z': terrain[coordinates[0]][coordinates[1]]}
    return position

def get_terrain(height, width):
    print('Build Terrain')
    global food, obstacles, terrain
    seed = datetime.datetime.now()
    seed = seed.hour + 24 * (seed.day + 31 * seed.month) * 4352 + 32454354
    terrain = build_landscape(height, width, seed=seed).tolist()
    for i in range(0, 15):
        obstacles[i] = get_random_coordinate(height)
    for j in range(0, 100):
        food[j] = get_random_coordinate(height)
    return terrain 

def get_all_players_on_start(): 
    for player in all_users:
        emit('requestPosition', {},  room=player)
        emit('spawn', {'id': player}, room=request.sid)

# Socket Listeners 

@socketio.on('connect')
def test_connect():
    global all_users, food, obstacles, microservices_urls, terrain
    print('connect with socket info', request.sid)
    get_all_players_on_start()
    all_users.append(request.sid)
    get_terrain(250, 250)
    # Alert other users of new user and load data for game start
    # print(food, obstacles)
    terrain = requests.get(microservices_urls["terrain"] + '/get_landscape')
    # requests.get(microservices_urls["terrain"] + '/get_landscape')
    # emit('load', {'terrain': terrain, 'food': food, 'obstacles': obstacles}, room=request.sid)
    # emit('spawn', {'id': request.sid}, broadcast=True, include_self=False)
    

@socketio.on('move')
def share_user_movement(json): 
    # print('send user movement to other users' + str(json) + request.sid)
    emit('playerMove', create_location_object(request.sid, json), broadcast=True, include_self=False)

@socketio.on('look')
def share_user_movement(json): 
    # print('send user movement to other users' + str(json) + request.sid)
    emit('otherPlayerLook',create_location_object(request.sid, json), broadcast=True, include_self=False)

@socketio.on('playerPosition')
def send_position_to_new_user(json):
    print('called this', json); 
    print('this should really only go to new user', request.sid); 
    emit('updatePosition', create_location_object(request.sid, json), broadcast=True)

@socketio.on('eat')
def regenerate_food(json):
    print('food eaten', json)
    food[json.id] = get_random_coordinate(250)
    food[json.id]['id'] = json.id
    emit('eaten', food[json.id], broadcast=True)

@socketio.on('collision')
def regenerate_obstacle(json): 
    print('obstacle hit', json)
    obstacles[json.id] = get_random_coordinate(250)
    obstacles[json.id]['id'] = json.id
    emit('collided', obstacles[json.id], broadcast=True)


# disconnect 

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected', request.sid)
    global all_users
    all_users.remove(request.sid)
    # if len(all_users) == 0:
    #     Timer(2.0, create_food).stop()
    
    emit('onEndSpawn', {'id': request.sid}, broadcast=True) # currently doens't de-render user

# error handling
@socketio.on_error()    
def error_handler(e):
    print('error', e)
    pass

@socketio.on_error_default
def default_error_handler(e):
    print('error', e)
    pass


if __name__ == '__main__':
    # socketio.run(app)
    eventlet.wsgi.server(eventlet.listen(('', 9000)), app, debug=True)
