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
import datetime

DEFAULT_PLAYER_MASS = 10
DEFAULT_BOOST_COST = 0.1
MINIMUM_BOOST_COST = 2.4
BOARD_WIDTH = 250
BOARD_HEIGHT = 250
MIN_PLAYERS_ZOMBIE_THRESHOLD = 0
DEFAULT_FOOD_MASS = 1

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

# Absolute path to the configuration file
app.config.from_envvar('APP_CONFIG_FILE')

socketio = SocketIO(app, async_mode='eventlet')

current_zombie_id = 0
terrain = None
maxFood = 100
# First, make sure we are working with a clean redis store
requests.get(app.config['DB_URL'] + '/flush', json={})


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



# On new client connection, create food, obstacles, landscape, and inialize player (on new client and others)
@socketio.on('connect')
def on_connect():
    global terrain
    print('NEW CONNECTION: ', request.sid)

    # Request for the terrain
    if terrain == None:
        seed = datetime.datetime.now()
        seed = seed.hour + 24 * (seed.day + 31 * seed.month) * 4352 + 32454354
        terrain = requests.get(app.config['TERRAIN_URL'] +
           '/get_landscape?width=' + str(BOARD_WIDTH) +
           '&height=' + str(BOARD_HEIGHT) +
           '&seed=' + str(seed)).json()['result']
    
    socketio.emit('landscape', {'terrain': terrain}, room=request.sid)
    # Request for field-objects: Response dealt with above
    requests.get(app.config['OBJECTS_URL'] + '/terrain_objects?width=' + str(BOARD_WIDTH) + '&height=' + str(BOARD_HEIGHT))

    # Spawn all other players into new player's screen (Must happen before initializing current player)
    playersList = requests.get(app.config['DB_URL'] + '/players/get_all').json()
    if playersList != None and len(playersList) > 0: 
        for player in playersList:
            emit('spawn', {'id': player['id'], 'mass': player['mass']}, room=request.sid)
    requests.post(app.config["DB_URL"] + '/users/add', json={'id': request.sid, 'zombies': []})
    requests.post(app.config['DB_URL'] + '/players/add', json={'mass': DEFAULT_PLAYER_MASS, 'id': request.sid})

    add_more_zombies()

def initialize_main_player(id):
    playerPositionX = random.random() * (BOARD_WIDTH - 20) + 10
    playerPositionZ = random.random() * (BOARD_HEIGHT - 20) + 10
    socketio.emit('initialize_main_player',
                  {'id': id,
                   'mass': DEFAULT_PLAYER_MASS,
                   'x': playerPositionX,
                   'z': playerPositionZ}, room=id)
    # Spawn new player on other 
    emit('spawn', {'id': id,
                   'mass': DEFAULT_PLAYER_MASS}, broadcast=True, include_self=False)
    # print('players count: ' + str(len(players)))


def add_more_zombies():
    global current_zombie_id
    users = requests.get(app.config["DB_URL"] + '/users/get_all').json()
    players = requests.get(app.config["DB_URL"] + '/players/get_all').json()
    if len(users) <= 0:
        return
    # create up to 20 zombies
    for i in range(max(0, MIN_PLAYERS_ZOMBIE_THRESHOLD - len(players))):
        # Choose a random client to add the zombie to
        user_id = random.choice(users)['id']
        zombieMass = DEFAULT_PLAYER_MASS - 2 -(1 + 2 * random.random())
        current_zombie_id += 1
        zombiePositionX = random.random() * (BOARD_WIDTH - 20) + 10
        zombiePositionZ = random.random() * (BOARD_HEIGHT - 20) + 10
        zombieID = 'zombie_' + str(current_zombie_id)
        socketio.emit('initialize_zombie_player',
                      {'id': zombieID, 
                       'mass': zombieMass,
                       'x': zombiePositionX,
                       'z': zombiePositionZ}, room=user_id)
        
        # Store zombie on assigned player 
        requests.post(app.config['DB_URL'] + '/users/add_zombie', json={'id': user_id, 'zombie': zombieID})
        # Store zombie as player
        requests.post(app.config["DB_URL"] + '/players/add', json = {'id': zombieID, 'mass': zombieMass})
        
        emit('spawn', {'id': zombieID, 'mass': zombieMass}, broadcast=True, include_self=False) 



# Updates all users when one client changes direction
@socketio.on('look')
def share_user_look_direction(json):
    # print('look: ' + request.sid)  
    emit('otherPlayerLook', dict({'id': request.sid}, **json), broadcast=True, include_self=False)

# Updates all users and reduces player mass when one client uses boost
@socketio.on('boost')
def share_user_boost_action(json):
    player_id = json['player_id']
    emit('otherPlayerBoost', {'id': player_id}, broadcast=True, include_self=False)
    player = requests.get(app.config['DB_URL'] + '/players/' + str(player_id)).json()
    player_mass = float(player[0]['mass'])
    new_mass = min(player_mass * (1 - DEFAULT_BOOST_COST), player_mass - MINIMUM_BOOST_COST)
    emit('player_mass_update', {'id': player_id, 'mass': new_mass}, broadcast=True, include_self=True)
    requests.post(app.config['DB_URL'] + '/players/add', json={'id': player_id, 'mass': new_mass })

# Updates other players on player state in regular intervals
@socketio.on('player_state_reconcile')
def relay_player_state(json):
    emit('otherPlayerStateInfo', json, broadcast=True, include_self=False)

# Message sent when a player is killed
@socketio.on('kill_player')
def kill(json): 
    id = json['id']
    emit('player_killed', {'id': id}, broadcast=True, include_self=True)
    requests.get(app.config['DB_URL'] + '/players/delete/' + id)
    # return 10 food items with id > 100
    # Range should be from 101 to 150
    data = requests.get(app.config['OBJECTS_URL'] + '/get_pi_food?x=' + str(json['x_position']) + '&z=' + str(json['z_position'])).json()
    print('data', data)
    emit('eaten', data , broadcast=True)
    add_more_zombies()

@socketio.on('initialize_main')
def initialize_main(json):
    initialize_main_player(request.sid)

    ## Create food
    ## Send Kill Player Signal

@socketio.on('eat')
def on_eat(json):
    global maxFood
    food_id = json['food_id']
    player_id = json['player_id']
    data = requests.get(app.config['OBJECTS_URL'] + '/update_object?type=food&id='+food_id).json()
    print('eat data', data)
    if (int(food_id) > maxFood):
        data = {'x': 0,'z': 0,'id': food_id}
    emit('eaten', {'food': [data] }, broadcast=True)
    player = requests.get(app.config['DB_URL'] + '/players/' + player_id).json()[0]
    new_mass = float(player['mass']) + DEFAULT_FOOD_MASS
    requests.post(app.config['DB_URL'] + '/players/add', json={'id': player_id, 'mass': new_mass })
    emit('player_mass_update', {'id': player_id, 'mass': new_mass}, broadcast=True, include_self=True)

@socketio.on('collision')
def regenerate_obstacle(json): 
    obstacle_id = json['obstacle_id']
    player_id = json['player_id']
    player = requests.get(app.config['DB_URL'] + '/players/' + player_id).json()[0]
    new_mass = max(float(player['mass']) * 0.75,  DEFAULT_PLAYER_MASS)
    requests.post(app.config['DB_URL'] + '/players/add', json={'id': player_id, 'mass': new_mass })
    emit('player_mass_update', {'id': player_id, 'mass': new_mass}, broadcast=True, include_self=True)
    emit('other_player_collided_with_obstacle', { 'player_id': player_id }, broadcast=True, include_self=False)


# disconnect 

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected', request.sid)
    emit('onEndSpawn', {'id': request.sid}, broadcast=True) # currently doens't de-render 
    user = requests.get(app.config['DB_URL'] + '/users/' + request.sid).json()[0]
    zombies = user['zombies'].split()
    for zombie_id in zombies:
        emit('onEndSpawn', {'id': zombie_id}, broadcast=True) # currently doens't de-render 
        requests.get(app.config['DB_URL'] + '/players/delete/' + zombie_id)
    requests.get(app.config['DB_URL'] + '/users/delete/' + request.sid)
    requests.get(app.config['DB_URL'] + '/players/delete/' + request.sid)
    add_more_zombies()

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
