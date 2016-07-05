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

  def test_disconnect(self):
      global disconnected
      disconnected = None
      client = socketio.test_client(app)
      client.disconnect()
      self.assertEqual(disconnected, '/')

if __name__ == '__main__':
    unittest.main()