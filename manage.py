import eventlet
eventlet.monkey_patch()

from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit, join_room
from ee_modules.landscape.fractal_landscape import fractal_landscape

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'



socketio = SocketIO(app, async_mode='eventlet')

all_users = []
user_count = 0


@app.route('/hello')
def index():
    return 'Welcome to Ethereal Epoch'

# Setup
def send_new_user_terrain():
    print('Build Terrain')
    # emit('load', {'terrain':fractal_landscape(300, 300, 300, 300, 4)}, room=request.sid) # emits just to new connecting user

def send_users_to_new_user(): 
    print('in send_users_to_new_user', request.sid)
    emit('requestPosition', broadcast=True)
    for player in all_users:
        print('call spawn event', player)
        # add check for already exists
        emit('spawn', {'id': player}, room=request.sid)


@socketio.on('connect')
def test_connect():
    global all_users, user_count
    print('connect with socket info', request.sid)
    user_count += 1
    send_users_to_new_user()
    all_users.append(request.sid)
    send_new_user_terrain()
    emit('spawn', {'id': request.sid, 'count': user_count}, broadcast=True, include_self=False)

@socketio.on('move')
def share_user_movement(json): 
    print('send user movement to other users' + str(json) + request.sid)
    x = json["x"]
    y = json["y"]
    z = json["z"]
    emit('playerMove', {'id': request.sid, 'x': x, 'y': y, 'z': z}, broadcast=True)

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

