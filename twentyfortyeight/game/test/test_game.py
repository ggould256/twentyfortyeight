import random
import unittest

from game.board import Board
from game.game import Game
from game.common import *


class TestBoard(unittest.TestCase):
    def setUp(self):
        self.basic_game = Game(board=None, rnd=random.Random(1))

    def test_constructor(self):
        self.assertEqual(self.basic_game.score(), 0)
        game = Game(rnd=random.Random(1))
        self.assertEqual(game.board(), self.basic_game.board())

    def test_smash(self):
        # This doesn't comprehensively test smashing because
        # the tests for Board mostly did that already.
        for direction in DIRECTIONS:
            board = Board()
            board = board.update((1, 1), 2)
            game = Game(rnd=random.Random(1), board=board)
            self.assertTrue(game.smash(direction))
            self.assertEqual(game.board()[1, 1], 0)
        for direction in DIRECTIONS:
            board = Board()
            board = board.update((0, 0), 2)
            game = Game(rnd=random.Random(1), board=board)
            if direction in {UP, LEFT}:
                self.assertFalse(game.smash(direction))
            else:
                self.assertTrue(game.smash(direction))
                self.assertEqual(game.board()[0, 0], 0)
