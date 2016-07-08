See [Shatter Land client repo](https://github.com/mellowDice/ee_client/blob/master/README.md) for full project overview. Below is subset of this repository's code:

## Primary Server and Movement Service
### Overview

Server's primary responsibility is to relay data between clients and pull data from other services in the network. On initial connection if terrain has not yet been saved in memory, server requests terrain from Landscape service and sends to the client. The server pulls all players and objects from the database and relays them to the new client. 

During gameplay, the server listens for player updates and sends data to the client. The client determines player physics and sends that to the server. The server is responsible for increasing and decreasing player mass on collisions between players and game objects like food and obstacles. 

The server relies on Redis to track all clients connected to the game as well as the zombie players that are spawned and 'owned' by all the connected clients. 

#### Technologies and dependencies
* Flask 
* Python 3.5
* Flask-Socket.io
* Numpy
* Requests
* Eventlet
* Flask Unit Tests
* Docker
* Circle CI

### Getting Started

Pull down Docker image to run server locally
``` 
$ docker pull erinkav/landscape-service
$ docker run --name landscape_service -d -p 7000:7000 -e APP_CONFIG_FILE='config/development.py' erinkav/landscape-service
```
### Listeners

| Incoming                     | Outgoing                                                                                        | Notes                                                                                                                                                  |
|------------------------------|-------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| on('connect')                | emit('landscape')  <br> get(/players)  <br> emit('spawn')  <br> post(/players)  <br>  post(/users)                       | Terrain data to client  <br> All players from DB  <br> Send each player to Client  <br> Save to players in DB <br> Save to users in DB                                        |
| on('look')                   | emit('otherPlayerLook')                                                                         | Relay directional data to all clients                                                                                                                  |
| on('boost')                  | emit('otherPlayerBoost') <br> emit('player_mass_update') <br>  post(/players)                              | Notify all clients of boost movement  <br>  Send decreased mass to all clients  <br> Update mass in player DB                                                       |
| on('player_state_reconcile') | emit('otherPlayerStateInfo')                                                                    | Relay movement and mass data to all clients                                                                                                            |
| on('kill_player')            | emit('player_killed') <br>  get(/players)  <br> get(/objects)  <br> emit('eaten')                                 | Relay event to all clients  <br> Delete player from DB <br>  Request terrain objects from object service  <br> Send new objects to all clients                           |
| on('initialize_main')        | emit('initialize_main_player')  <br> emit('spawn')                                                    | Initialize main player on client  <br> Send new player to all other clients                                                                                  |
| on('eat')                    | get(/objects)  <br> emit('eaten')  <br> get(/players) post(/players)  <br> emit('player_mass_update)              |  Get new location from Object service  <br> Relay new location to clients  <br> Get player data from DB  <br> Update player mass in DB  <br> Send new mass to all clients      |
| on('collision')              | get(/player)  <br> post(/player)  <br> emit(player_mass_update)  <br> emit(other_player_collided_with_obstacle)   | Get player data from DB <br>  Update player mass in DB <br>  Send new mass to all clients  <br> Send collision event to all clients                                      |
| on('disconnect')             | emit('onEndSpawn')  <br> get(/users)  <br> emit('onEndSpawn') *Zombie characters*  <br> get(/users)  <br> get(/players) | Send disconnect event to all clients  <br> Get user's zombie players  <br> Send zombie disconnect to clients  <br> Delete user from database  <br> Delete from player database |
