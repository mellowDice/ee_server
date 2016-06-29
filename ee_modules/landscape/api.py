from flask import Flask
import requests
from fractal_landscape import build_landscape

app = Flask(__name__)

import datetime

@app.route('/get_landscape')
def get_landscape():
    seed = datetime.datetime.now()
    seed = seed.hour + 24 * (seed.day + 31 * seed.month) * 4352 + 32454354
    print(build_landscape)
    requests.post('http://localhost:9000/send_terrain', json = {'terrain':build_landscape(10, 10, seed=seed).tolist()})
    return 'OK'

if __name__ == '__main__':
    app.run(port=7000, debug=True)
