"""Rules for the game of 2048."""

import copy
import random

from .board import Board
from .common import (STARTING_TILES, HEIGHT, WIDTH,
                     TILE_FREQ, OK, GAMEOVER, ILLEGAL)


class Game(object):
    """A class representing a game in progress.  Also contains some public
    static constants of use to other classes."""

    def __init__(self, board=None, rnd=None, score=0):
        self._rnd = rnd if rnd is not None else random.Random()
        self._score = score
        if board is None:
            self._board = Board()
            for t in STARTING_TILES:
                self._add_tile(t)
        else:
            self._board = board

    def __repr__(self):
        return ("Game(%s, %s, %s)" %
                (self._board, self._rnd.getstate(), self._score))

    def pretty_print(self):
        print(self._score)
        self._board.pretty_print()

    def board(self):
        return self._board

    def score(self):
        return self._score

    def _add_tile(self, tile_value=None):
        open_spaces = {(x, y)
                       for y in range(HEIGHT)
                       for x in range(WIDTH)
                       if not self._board[(x, y)]}
        if not open_spaces:
            return False
        r = self._rnd.random()
        if tile_value is None:
            for (tile, freq) in TILE_FREQ:
                tile_value = tile
                if r < freq:
                    break
                else:
                    r -= freq
        (new_x, new_y) = self._rnd.sample(open_spaces, 1)[0]
        self._board = self._board.update((new_x, new_y), tile_value)
        return True

    # This method is broken out because in principle it might be used to
    # run large number of games at high performance:  Because all rotations
    # are equally valuable game states, the only reason to do the
    # counterrotate is to present a consistent state for a human or other
    # stateful user.
    def _smash_without_counterrotate(self, direction):
        """Smashes in the given direction, leaving the board rotated
        with direction pointed up.  Returns True iff the smash actually
        changed anything other than the rotation."""
        new_board = copy.deepcopy(self._board)
        for _ in range(direction):
            new_board = new_board.rotate_cw()
        changed, turn_score, new_board = new_board.smash_up()
        if not changed:
            return False  # Illegal move
        self._score += turn_score
        self._board = new_board
        return True

    def smash(self, direction):
        """Performs, end-to-end, the smash phase of the turn."""
        changed = self._smash_without_counterrotate(direction)
        new_board = self._board
        for _ in range(direction):
            new_board = new_board.rotate_ccw()
        self._board = new_board
        return changed

    def do_turn(self, direction):
        """Perform a "smash" in the indicated direction, add a random tile,
        and return the result."""
        _, result = self.do_turn_and_retrieve_intermediate(direction)
        return result

    def do_turn_and_retrieve_intermediate(self, direction):
        """Just like do_turn but also returns the state of the board before
        the tile add step (as this is typically what will be wanted for a
        machine learning Q function."""
        smashed = self.smash(direction)
        if not smashed:
            # print "ILLEGAL MOVE"  # Verbosity for debugging
            return None, ILLEGAL
        intermediate_board = self._board
        added = self._add_tile()
        if added:
            # self.pretty_print()  # Verbosity for debugging
            if self._board.can_move():
                return intermediate_board, OK
            else:
                return intermediate_board, GAMEOVER
        else:
            # This branch can't happen if Board.can_move() is implemented
            # correctly.
            assert False
