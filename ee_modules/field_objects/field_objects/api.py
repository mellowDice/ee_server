from flask import Flask, request
import requests
from create_terrain_objects import save_terrain, create_or_update_terrain_object, get_all_food, get_all_obstacles

app = Flask(__name__)

@app.route('/terrain_objects', methods=['GET'])
def get_terrain_objects():
    print('food', get_all_food(), 'obstacles', get_all_obstacles())
    requests.post('http://localhost:9000/send_field_objects', json ={'food':get_all_food(), 'obstacles': get_all_obstacles()})
    return 'OK'

@app.route('/update_object', methods=['GET'])
def update_object():
    objId = request.args.get('id')
    objType = request.args.get('type')
    # data = create_or_update_terrain_object(objType, objId)
    # return data
    return objId + objType

@app.route('/store_terrain', methods=['POST'])
def save_landscape():
    # terrain = request.json["terrain"]
    height = 250
    width = 250
    save_terrain(height, width, request.json["terrain"])
    return 'Ok'


if __name__ == '__main__':
    app.run(port=7001, debug=True)