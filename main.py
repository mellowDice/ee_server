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
BOARD_WIDTH = 250
BOARD_HEIGHT = 250

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

app.config.from_object('config.development')
# Absolute path to the configuraiton file
app.config.from_envvar('APP_CONFIG_FILE')

socketio = SocketIO(app, async_mode='eventlet')

user_count = 0
currentZombieID = 0
food = {}
obstacles = {}
players = {}

@app.route('/')
def index():
    return 'Welcome to Ethereal Epoch'

# Response from field-objects service
@app.route('/send_field_objects', methods=['POST'])
def field_object_creator(): 
    food = request.json["food"]
    obstacles = request.json["obstacles"]
    socketio.emit('field_objects',
                  {'food': food, 
                   'obstacles': obstacles})
    return 'Ok'

# Helper function to get all player information
def get_all_players_on_start(): 
    for id in players:
        # emit('requestPosition', {},  room=id)
        emit('spawn', {'id': id, 'mass': players[id]['mass']}, room=request.sid)

# On new client connection, create food, obstacles, landscape, and inialize player (on new client and others)
@socketio.on('connect')
def on_connect():
    global currentZombieID
    print('NEW CONNECTION: ', request.sid)

    # Request all player info to populate new player's screen
    get_all_players_on_start()

    # Request for the terrain
    terrain = requests.get(app.config['TERRAIN_URL'] + '/get_landscape').json()
    socketio.emit('landscape', {'terrain': list(terrain)}, room=request.sid)

    # Request for field-objects: Response dealt with above
    requests.get(app.config['OBJECTS_URL'] + '/terrain_objects')

    # Initialize current player
    mass = DEFAULT_PLAYER_MASS * random.random()
    players[request.sid] = {'mass': mass, 'zombies': []}
    socketio.emit('initialize_main_player',
                  {'id': request.sid, 
                   'mass': mass}, room=request.sid)
    # Spawn new player on other clients
    emit('spawn', {'id': request.sid, 'mass': mass}, broadcast=True, include_self=False)


    # Create a zombie player per user
    zombieMass = DEFAULT_PLAYER_MASS * random.random()
    currentZombieID += 1
    zombiePositionX = random.random() * BOARD_WIDTH
    zombiePositionZ = random.random() * BOARD_HEIGHT
    zombieID = 'zombie' + str(currentZombieID)
    socketio.emit('initialize_zombie_player',
                  {'id': zombieID, 
                   'mass': 20,
                   'x': zombiePositionX,
                   'z': zombiePositionZ}, room=request.sid)
    players[zombieID] = {'mass': zombieMass}
    players[request.sid]['zombies'].append(zombieID)
    emit('spawn', {'id': zombieID, 'mass': mass}, broadcast=True, include_self=False)
    print('finsihed spawning zombie ' + zombieID)


# Updates all clients when one client changes direction
@socketio.on('look')
def share_user_look_direction(json):
    # print('look: ' + request.sid)  
    emit('otherPlayerLook', dict({'id': request.sid}, **json), broadcast=True, include_self=False)

# Updates all clients and reduces player mass when one client uses boost
@socketio.on('boost')
def share_user_boost_action(json):
    emit('otherPlayerBoost', {'id': request.sid}, broadcast=True, include_self=False);
    emit('playerMassUpdate', {'id': request.sid, 'mass': players[request.sid]['mass'] - DEFAULT_BOOST_COST})

# Updates other players on player state in regular intervals
@socketio.on('player_state_reconcile')
def relay_player_state(json):
    emit('otherPlayerStateInfo', dict({'id': request.sid}, **json), broadcast=True, include_self=False)

# Message sent when a player is killed
@socketio.on('kill_player')
def kill(json): 
    print('player killed', json)
    emit('player_killed', {'id': json['id']}, broadcast=True, include_self=True)
    ## Create food
    ## Send Kill Player Signal

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


# disconnect 

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected', request.sid)
    emit('onEndSpawn', {'id': request.sid}, broadcast=True) # currently doens't de-render 
    for zombie in players[request.sid].setdefault('zombies', []):
        emit('onEndSpawn', {'id': zombie}, broadcast=True) # currently doens't de-render 
        del players[zombie]
    del players[request.sid]

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
