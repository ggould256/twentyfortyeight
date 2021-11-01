import random

from twentyfortyeight.game.common import DIRECTIONS
from .strategy import Strategy

class RandomStrategy(Strategy):
    def __init__(self, rnd=None):
        self._rnd = rnd if rnd is not None else random.Random()

    def get_move(self, board, score):
        return self._rnd.choice(DIRECTIONS)


class SpinnyStrategy(Strategy):
    def __init__(self):
        self._counter = 0

    def get_move(self, board, score):
        self._counter += 1
        return DIRECTIONS[self._counter % len(DIRECTIONS)]
