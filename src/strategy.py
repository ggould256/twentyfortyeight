"""An interface for 2048 strategy modules, and several examples of
strategies."""

import random
from rules import Game


class Strategy(object):
    """An abstract class for 2048 strategies.  Implementers will wish
    to override at least get_move().  A strategy will be instantiated
    once at the beginning of each games, and disposed of once the game is
    complete."""

    def name(self):
        """@return a name that can be used in printing messages about this
        strategy"""
        return self.__class__.__name__

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
