import unittest
from flask import Flask, request, render_template
from flask_socketio import SocketIO, send, emit, join_room
from main import *
import coverage

cov = coverage.coverage()
cov.start()

class TestSockets(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
      pass

  @classmethod
  def tearDownClass(cls):
      cov.stop()
      cov.report(include='flask_socketio/__init__.py')

  def setUp(self):
      pass

  def test_connection(self):
      client = socketio.test_client(app)
      received = client.get_received()
      self.assertEqual(len(received), 1)
      self.assertEqual(received[0]['args'], 'connected')
      client.disconnect()

  def test_add_player(self):
      test_player = {'id': 1, 'mass': 1, 'zombies': None}
      requests.post(app.config['DB_URL'] + '/users/add')
      received = requests.get(app.config['DB_URL'] + '/users/' + str(test_player['id']))
      print(received.json())
      self.assertEqual(received.json(), test_player)
  
  def test_disconnect(self):
      # Confirm not in database 
      # global disconnected
      # disconnected = None
      # client = socketio.test_client(app)
      # client.disconnect()
      # self.assertEqual(disconnected, '/')

  def test_user_storage_on_connect(self):
      # Confirm user exists in database on connect

  def test_zombies_created(self):
      # Confirm zombies exist on connect

  def test_boost(self):
      # On boost emit test to see whether player mass is less than previous player mass

  def test_kill_player(self):
      # on kill player emit
      # Confirm player does not exist in database

  def test_eat(self):
      #confirm object in database location changed
      # confirm eaten was called

  def test_collision(self):
      #confirm object in database location changed
      # confirm collided was called

  def test_zombie_removed_on_disconnect(self):
      # when user disconnects, confirm if its zombies are in player



if __name__ == '__main__':
    unittest.main()