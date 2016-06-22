import eventlet
from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit, join_room
from threading import Thread
from ee_modules.landscape.fractal_landscape import fractal_landscape

eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

all_users = []
user_count = 0
# store all at current time

@app.route('/hello')
def index():
    return 'Welcome to Ethereal Epoch'

# Setup
def send_new_user_data():
    emit('load', {'users': all_users, 'terrain':fractal_landscape(300, 300, 300, 300, 4)}, room=request.sid) # emits just to new connecting user
    print('id available in callback', request.sid) # user's session id

@socketio.on('connect')
def test_connect():
    # Does a logged in user get the ids of every user on the page? 
    # Does a second user send a new spawn event to every other user?
    global all_users, user_count
    print('connect with socket info', request.sid)
    user_count += 1
    all_users.append(request.sid)
    send_new_user_data()
    emit('spawn', {'id': request.sid, 'count': user_count}, broadcast=True)

@socketio.on('move')
def share_user_movement(json): 
    print('send user movement to other users' + str(json) + request.sid)
    #Get users from DB and send data to each
    emit('move', {'id': request.sid, 'coordinates': json}, broadcast=True)

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



# @app.route('/', methods=['GET']) # replace with socket
# def load():#spawn broadcast
# #loaded
# #sessions
#     # call map generation service
#     return 'Map sent to client'

# @app.route('/friends')
# def getfriends():
#     # call to DB
#     return 'Friends sent to client'



# # request landscape
# @socketio.on('request_landscape')
# def handle_landscape_request(json):
#     print('received landscape request')
#     emit('landscape_matrix', {data: fractal_landscape(300, 300, 300, 300, 8)})
