"""An interface for 2048 strategy modules, and several examples of
strategies."""

import random
from rules import Game

class Strategy(object):
    """An abstract class for 2048 strategies.  Implementors will wish
    to override get_move().  A strategy will be instantiated once at
    the beginning of each games, and disposed of once the game is
    complete."""

    def get_move(self, board, score):
        """
        Given the current state of the game, return the move chosen by
        this strategy.  Subclasses must implement this method.
        """
        raise NotImplementedError(
            "Strategy subclasses must implement get_move().")

    def notify_outcome(self, board, score):
        """Optionally, subclasses may choose to be notified of the
        outcome of the game.  This is your opportunity to gloat."""
        pass

class RandomStrategy(Strategy):
    def __init__(self):
        self._rnd = random.Random()

    def get_move(self, board, score):
        return self._rnd.choice(Game.DIRECTIONS)


class SpinnyStrategy(Strategy):
    def __init__(self):
        self._counter = 0

    def get_move(self, board, score):
        self._counter += 1
        return Game.DIRECTIONS[self._counter % len(Game.DIRECTIONS)]

    def notify_outcome(self, board, score):
        best_tile = max(max(column) for column in board)
        if best_tile >= 2048:
            print "Oh yeah, I rock, I got a", best_tile
        else:
            print "Oops, I only got", best_tile
