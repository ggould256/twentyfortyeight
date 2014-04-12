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
def _sum_dicts(dicts):
    if not dicts:
        return {}
    else:
        left = dicts[0].copy()
        right = _sum_dicts(dicts[1:])
        keys = set(left.iterkeys())
        keys |= set(right.iterkeys())
        result = {key: (left.get(key, 0) + right.get(key, 0))
                  for key in keys}
        return result


class Lookahead(object):
    def __init__(self, distribution):
        self._preimage = distribution

    def after_move(self, move):
        return {board.apply_move(move): probability
                for (board, probability) in self._preimage}

    def after_placement(self):
        # This is kinda inefficient; rewrite with _sum_dicts/comprehension
        # stack.  Or at least loop-reordering.
        postimage = {}
        for (tile, tile_probability) in Game.TILE_FREQ:
            for (board, board_probability) in self._preimage.items():
                open_spaces = board.open_spaces()
                for loc in open_spaces:
                    new_board = board.update(loc, tile)
                    postimage[new_board] = (
                        postimage.get(new_board, 0) +
                        (tile_probability * board_probability *
                         (1.0 / len(open_spaces))))
        return postimage
