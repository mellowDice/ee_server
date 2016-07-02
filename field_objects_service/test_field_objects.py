from unittest import TestCase

import create_food

class TestFieldObjects(TestCase):
    def test_coordinates(self):
      s = create_food.save_terrain()
      # self.assertTrue(isinstance(s, basestring))