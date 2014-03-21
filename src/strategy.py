"""An interface for 2048 strategy modules, and several examples of
strategies."""

import random
from rules import Game

class Strategy(object):
    """An abstract class for 2048 strategies.  Implementors will wish
    to override get_move()."""

    def get_move(self, board, score):
        raise NotImplementedError(
            "Strategy subclasses must implement get_move().")


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
