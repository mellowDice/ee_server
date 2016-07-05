# Hooks
# Session
# Error Handling
# Testing
# 
import eventlet
eventlet.monkey_patch()
import traceback
from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit, join_room
import requests
import numpy as np
import random

DEFAULT_PLAYER_MASS = 100
DEFAULT_BOOST_COST = 2.5

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

app.config.from_object('config.development')
# Absolute path to the configuraiton file
app.config.from_envvar('APP_CONFIG_FILE')

socketio = SocketIO(app, async_mode='eventlet')

all_users = []
user_count = 0
food = {}
obstacles = {}
terrain = {}
players = {}

@app.route('/')
def index():
    return 'Welcome to Ethereal Epoch'

# @app.route('/send_terrain', methods=['POST'])
# def terrain_creator(*args,  **kwargs):
#     global terrain
#     # print('terrain creator', request.json["terrain"])
#     # print('response', r.json(), args['proxies'])
#     terrain = request.json["terrain"]

#     requests.get(app.config['OBJECTS_URL'] + '/terrain_objects')

#     ### ADB: Send field objects to user
#     return 'Ok'

@app.route('/send_field_objects', methods=['POST'])
def field_object_creator(): 
    global terrain
    food = request.json["food"]
    obstacles = request.json["obstacles"]
    print('obstacles', obstacles)
    print('food', food)
    # print('terrain', terrain)
    # print('Terrain called globally', list(terrain[:1]))

    socketio.emit('field_objects',
                  {'food': food, 
                   'obstacles': obstacles})
    print('field_objects socket emit should have happened')
    return 'Ok'

    
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

def get_all_players_on_start(): 
    for id in players:
        emit('requestPosition', {},  room=id)
        emit('spawn', {'id': id, 'mass': players[id]['mass']}, room=request.sid)

@socketio.on('connect')
def test_connect():
    global all_users, food, obstacles, microservices_urls, terrain
    print('connect with socket info', request.sid)
    get_all_players_on_start()
    all_users.append(request.sid)
    print(app.config)
    # get_terrain(250, 250)
    # Alert other users of new user and load data for game start
    # print(food, obstacles)
    # requests.get(microservices_urls["terrain"] + '/get_landscape', hooks=dict(response=terrain_creator))
    response = requests.get(app.config['TERRAIN_URL'] + '/get_landscape')
    terrain = response.json()
    socketio.emit('landscape', {'terrain': list(terrain)}, room=request.sid)
    # socketio.emit('landscape', {'terrain': list(terrain),
    #               'food': food, 
    #               'obstacles': obstacles}, broadcast=True)
    # terrain = data
    # print(data[0])
    requests.get(app.config['OBJECTS_URL'] + '/terrain_objects')

    mass = DEFAULT_PLAYER_MASS * random.random()
    socketio.emit('initialize_main_player',
                  {'id': request.sid, 
                   'mass': mass}, room=request.sid)
    players[request.sid] = {'mass': mass}
    emit('spawn', {'id': request.sid, 'mass': mass}, broadcast=True, include_self=False)
    # requests.get(app.config['']["terrain"] + '/get_landscape')

    # # place items on the map (TODO: fix hardcoded height)
    # height = 250
    # for i in range(0, 15):
    #     obstacles[i] = get_random_coordinate(height)
    # for j in range(0, 100):
    #     food[j] = get_random_coordinate(height)


    # mass = DEFAULT_PLAYER_MASS * random.random()
    # print("mass ",  mass)
    # emit('load', {'id': request.sid, 'mass': mass, 'terrain': terrain, 'food': food, 'obstacles': obstacles}, room=request.sid)
    # # emit('player_mass_update', {'id': request.sid, 'mass': mass})
    # players[request.sid] = {'mass': mass}


@socketio.on('move')
def share_user_movement(json): 
    # print('send user movement to other users' + str(json) + request.sid)
    emit('playerMove', create_location_object(request.sid, json), broadcast=True, include_self=False)

# @socketio.on('look')
# def share_user_movement(json): 
#     # print('send user movement to other users' + str(json) + request.sid)
#     emit('otherPlayerLook',create_location_object(request.sid, json), broadcast=True, include_self=False)
@socketio.on('look')
def share_user_look_direction(json):
    # print('look: ' + request.sid)  
    emit('otherPlayerLook', dict({'id': request.sid}, **json), broadcast=True, include_self=False)

@socketio.on('boost')
def share_user_boost_action(json):
    emit('otherPlayerBoost', {'id': request.sid}, broadcast=True, include_self=False);
    emit('playerMassUpdate', {'id': request.sid, 'mass': players[request.sid]['mass'] - DEFAULT_BOOST_COST})

@socketio.on('player_state_reconcile')
def relay_player_state(json):
    # print('state: ' + request.sid) 
    emit('otherPlayerStateInfo', dict({'id': request.sid}, **json), broadcast=True, include_self=False)

@socketio.on('playerPosition')
def send_position_to_new_user(json):
    print('called this', json); 
    print('this should really only go to new user', request.sid); 
    # emit('updatePosition', create_location_object(request.sid, json), broadcast=True)

@socketio.on('eat')
def regenerate_food(json):
    print('food eaten', json)
    data = requests.get(app.config['OBJECTS_URL'] + '/update_object?type=food&id='+json.id)
    food[json.id] = data
    emit('eaten', food[json.id], broadcast=True)

@socketio.on('collision')
def regenerate_obstacle(json): 
    print('obstacle hit', json)
    data = requests.get(app.config['OBJECTS_URL'] + '/update_object?type=obstacle&id='+json.id)
    obstacles[json.id]['id'] = json.id
    emit('collided', obstacles[json.id], broadcast=True)

@socketio.on('kill_player')
def kill(json): 
    print('player killed', json)
    emit('player_killed', {'id': json['id']}, broadcast=True, include_self=True)
    ## Create food
    ## Send Kill Player Signal

# disconnect 

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected', request.sid)
    global all_users
    all_users.remove(request.sid)
    emit('onEndSpawn', {'id': request.sid}, broadcast=True) # currently doens't de-render user
    del players[request.sid];

# error handling
@socketio.on_error()    
def error_handler(e):
    print('error', e, traceback.format_exc())

    pass

@socketio.on_error_default
def default_error_handler(e):
    print('error', e, traceback.format_exc())
    pass


if __name__ == '__main__':
    # socketio.run(app)
    eventlet.wsgi.server(eventlet.listen(('', 9000)), app, debug=True)
