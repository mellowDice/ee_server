from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit
from ee_modules.landscape.fractal_landscape import fractal_landscape

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

user_count = 0

@app.route('/')
def index():
    return 'You did it'

# Setup
def store_user():
    print(request.sid) # user's session id
    # Connect DB and store user
    user_count += 1 # User id placeholder
    return user_count

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

# request landscape
@socketio.on('request_landscape')
def handle_landscape_request(json):
    print('received landscape request')
    emit('landscape_matrix', {data: fractal_landscape(300, 300, 300, 300, 8)})

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
    user_count -= 1
    return user_count

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
    socketio.run(app, debug=True)



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
