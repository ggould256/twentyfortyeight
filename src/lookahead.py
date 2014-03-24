"""A module for looking ahead from the current game state to possible
future game states, as might be used to build and search a game tree.

Throughout this file the term "distribution" is used.  A distribution is
a dict (board state -> probability) describing a probability distribution
of possible future boards.
"""

from rules import Game


def lookahead_from(board):
    """A convenience factory for building a Lookahead object from a single
    board."""
    return Lookahead({board: 1.0})


# Convenience function
def _merge_dicts(*dicts):
    if not dicts:
        return {}
    else:
        result = dicts[0].copy()
        result.update(_merge_dicts(dicts[1:]))
        return result


class Lookahead(object):
    def __init__(self, distribution):
        self._preimage = distribution

    def after_move(self, move):
        return {board.apply_move(move): probability
                for (board, probability) in self._preimage}

    def after_placement(self):
        pass

# TODO finish this file
