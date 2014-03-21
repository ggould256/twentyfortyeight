"""Rules for the game of 2048."""

import random


def list_zip(*args):
    return map(list, zip(*args))

def rotate_cw(board):
    """Rotates a rectangular list of lists 'clockwise' (assuming
    board[x][y] is laid out in screen coordinates, ie with x
    increasing right and y increasing down)."""
    return list(reversed(list_zip(*board)))

def rotate_ccw(board):
    """Rotates a rectangular list of lists 'counterclockwise'
    (assuming board[x][y] is laid out in screen coordinates, ie with x
    increasing right and y increasing down)."""
    return list(list_zip(*reversed(board)))

def smash_up(board):
    """As when one presses the 'up'-arrow in the game: Shifts all
    columns upward to the extent possible by combining pairs of
    like tiles.  Assumes a board in screen coordinate style.

    Returns (score, board) -- the score of this move (the total value
    of all tiles created) and the new board resulting."""
    score = 0
    new_board = []
    for col in board:
        old_col = list(col)
        unzeroed = [v for v in old_col if v != 0]
        new_col = []
        while unzeroed:
            if len(unzeroed) > 1 and unzeroed[0] == unzeroed[1]:
                new_col.append(unzeroed[0] * 2)
                score += unzeroed[0] * 2
                unzeroed = unzeroed[2:]
            else:
                new_col.append(unzeroed[0])
                unzeroed = unzeroed[1:]
        new_col += [0] * (Game.HEIGHT - len(new_col))
        new_board.append(new_col)
    return (score, new_board)


class Game(object):
    WIDTH = 4
    HEIGHT = 4
    STARTING_TILES = [2, 2]
    TILE_FREQ = [ (2, 0.75), (4, 0.25) ]
    PRETTY_PRINT = { 0: ' ', 2: '2', 4: '4', 8: '8',
                     16: 'A', 32: 'B', 64: 'C', 128: 'D',
                     256: 'E', 512: 'F', 1024: 'G',
                     2048: 'H', 4096: 'I', 8192: 'J' }
    UP, LEFT, DOWN, RIGHT = range(4)


    def __init__(self, board=None, rnd=None, score=0):
        self._rnd = rnd if rnd is not None else random.Random()
        self._board = [[0 for y in range(Game.HEIGHT)]
                       for x in range(Game.WIDTH)]
        self._score = score

    def __repr__(self):
        return ("Game(" + self._board + ", " +
                self._rnd.getstate() + ", " + self._score + ")")

    def prettyprint(self):
        print "+-" + ("--" * Game.WIDTH) + "+"
        for y in range(Game.HEIGHT):
            line = "| "
            for x in range(Game.WIDTH):
                line += Game.PRETTY_PRINT[self._board[x][y]] + " "
            line += "|"
            print line
        print "+-" + ("--" * Game.WIDTH) + "+"

    def add_tile(self):
        open_spaces = { (x, y)
                        for y in range(Game.HEIGHT)
                        for x in range(Game.WIDTH)
                        if not self._board[x][y] }
        if not open_spaces:
            return False
        r = self._rnd.random()
        tile_value = None
        for (tile, freq) in Game.TILE_FREQ:
            tile_value = tile
            if r < freq:
                break;
            else:
                r -= freq
        (new_x, new_y) = self._rnd.sample(open_spaces, 1)[0]
        self._board[new_x][new_y] = tile_value
        return True

    def smash(self, direction):
        new_board = self._board
        for i in range(direction):
            new_board = rotate_cw(new_board)
        (turn_score, new_board) = smash_up(new_board)
        self._score += turn_score
        for i in range(direction):
            new_board = rotate_ccw(new_board)
        self._board = new_board

    def do_turn(self, direction):
        self.smash(direction)
        if self.add_tile():
            self.prettyprint()
            return True
        else:
            print "GAME OVER"
            return False
