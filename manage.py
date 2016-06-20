from flask import Flask, request
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# Setup
def store_user():
    # Connect DB and store user
    return 1 # User id placeholder

@socketio.on('connect')
def test_connect():
    print(request.sid)
    emit('my response', {'data': 'Connected'}, callback=store_user)

# Broadcast to client
@socketio.on('user_movement')
def handle_user_movement(json):
    print('received json: ' + str(json))
    # Call service
    emit('my response', json, broadcast=True)#broadcasts messages to user. also works with send
    share_user_movement(json)

def share_user_movement(json): 
    print('send user movement to other users' + str(json))
    #Get users from DB and send data to each
    emit('my response', json, namespace='/')
# Listen for client data

@socketio.on('message') # String data
def handle_message(message):
    print('received message: ' + message)

@socketio.on('json') # JSON data
def handle_json(json):
    print('received json: ' + str(json))

# disconnect 

@socketio.on('disconnect', namespace='/chat')
def test_disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)



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
