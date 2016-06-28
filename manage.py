import eventlet
eventlet.monkey_patch()

from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit, join_room
from ee_modules.landscape.fractal_landscape import build_landscape
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'


socketio = SocketIO(app, async_mode='eventlet')

all_users = []
user_count = 0


@app.route('/hello')
def index():
    return 'Welcome to Ethereal Epoch'

# Helper Functions

def create_location_object(user_id, data):
    x = data["x"]
    y = data["y"]
    z = data["z"]
    return {'id': user_id, 'x': x, 'y': y, 'z': z}

def get_terrain():
    print('Build Terrain')
    seed = datetime.datetime.now()
    seed = seed.hour + 24 * (seed.day + 31 * seed.month) * 4352 + 32454354
    return build_landscape(250, 250, seed=seed).tolist()

def get_all_players_on_start(): 
    for player in all_users:
        emit('requestPosition', {},  room=player)
        emit('spawn', {'id': player}, room=request.sid)

# Socket Listeners 

@socketio.on('connect')
def test_connect():
    global all_users, user_count
    print('connect with socket info', request.sid)
    get_terrain()
    get_all_players_on_start()
    all_users.append(request.sid)
    # Alert other users of new user and load data for game start
    emit('load', {'terrain': get_terrain()}, room=request.sid)
    emit('spawn', {'id': request.sid}, broadcast=True, include_self=False)
    

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

# disconnect 

@socketio.on('disconnect')
def disconnect():
    print('Client disconnected', request.sid)
    global user_count
    user_count -= 1
    all_users.remove(request.sid)
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
    eventlet.wsgi.server(eventlet.listen(('', 6000)), app, debug=True)
