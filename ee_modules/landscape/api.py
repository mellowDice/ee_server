from flask import Flask
import requests
from fractal_landscape import build_landscape

app = Flask(__name__)

import datetime

microservices_urls = {
    'terrain': 'http://localhost:7000',
    'field_objects': 'http://localhost:7001',
    'socket': 'http://localhost:9000'
}

@app.route('/get_landscape')
def get_landscape():
    seed = datetime.datetime.now()
    seed = seed.hour + 24 * (seed.day + 31 * seed.month) * 4352 + 32454354
    print('Session ', str(requests.Session()))
    terrain = build_landscape(10, 10, seed=seed).tolist()

    requests.post(microservices_urls['field_objects']+'/store_terrain', json = {'terrain':terrain})
    
    requests.post(microservices_urls['socket']+'/send_terrain', json = {'terrain':terrain})
    # Delete once stored in Redis
    return 'OK'

if __name__ == '__main__':
    app.run(port=7000, debug=True)
