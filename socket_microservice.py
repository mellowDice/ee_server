# Hooks
# Session
# Error Handling
# Testing
# 
import eventlet
eventlet.monkey_patch()

from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit, join_room
import requests
# import json
# import erequests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'

microservices_urls = {
    'terrain': 'http://localhost:7000',
    'field_objects': 'http://localhost:7001'
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
    terrain = request.json["terrain"]
    requests.get(microservices_urls['field_objects'] + '/terrain_objects')
    return 'Ok'

@app.route('/send_field_objects', methods=['POST'])
def field_object_creator(): 
    global terrain
    food = request.json["food"]
    obstacles = request.json["obstacles"]
    socketio.emit('load', {'terrain': terrain, 
                  'food': food, 
                  'obstacles': obstacles}, broadcast=True)
    return 'Ok'

    
# Helper Functions

def create_location_object(user_id, data):
    x = data["x"]
    y = data["y"]
    z = data["z"]
    return {'id': user_id, 'x': x, 'y': y, 'z': z}

def get_all_players_on_start(): 
    for player in all_users:
        emit('requestPosition', {},  room=player)
        emit('spawn', {'id': player}, room=request.sid)

# Socket Listeners 
def print_response(r, **kwargs):
    print(r.content, kwargs);

@socketio.on('connect')
def test_connect():
    global all_users, food, obstacles, microservices_urls, terrain
    print('connect with socket info', request.sid)
    get_all_players_on_start()
    all_users.append(request.sid)
    # get_terrain(250, 250)
    # Alert other users of new user and load data for game start
    # print(food, obstacles)
    requests.get(microservices_urls["terrain"] + '/get_landscape', hooks=dict(response=print_response))
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
    data = requests.get(microservices_urls["field_objects"] + '/update_object?type=food&id='+json.id)
    food[json.id] = data
    emit('eaten', food[json.id], broadcast=True)

@socketio.on('collision')
def regenerate_obstacle(json): 
    print('obstacle hit', json)
    data = requests.get(microservices_urls["field_objects"] + '/update_object?type=obstacle&id='+json.id)
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
