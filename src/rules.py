"""Rules for the game of 2048."""

import copy
import random


# Utility function
def list_zip(*lists):
    """Zip some @p lists, returning the result as a list of lists."""
    return list(map(list, zip(*lists)))


class Board(object):
    """An immutable class representing an arrangement of tiles on the game
    board.
    """
    def __init__(self, cols_data=None):
        if cols_data is None:
            self._cols = [[0 for _ in range(Game.HEIGHT)]
                          for _ in range(Game.WIDTH)]
        else:
            self._cols = [[cols_data[x][y] for y in range(Game.HEIGHT)]
                          for x in range(Game.WIDTH)]

    def __getitem__(self, location=None):
        """Allow indexing by coordinates, eg board[(x,y)]."""
        (x, y) = location
        return self._cols[x][y]

    def prettyprint(self):
        print("+-" + ("--" * Game.WIDTH) + "+")
        for y in range(Game.HEIGHT):
            line = "| "
            for x in range(Game.WIDTH):
                line += Game.PRETTY_PRINT[self._cols[x][y]] + " "
            line += "|"
            print(line)
        print("+-" + ("--" * Game.WIDTH) + "+")

    def column(self, x):
        """Returns the xth column."""
        return list(self._cols[x])

    def row(self, y):
        """Returns the yth row."""
        return (self._cols[x][y] for x in range(Game.WIDTH))

    def columns(self):
        """Returns the columns."""
        return (self.column(i) for i in range(Game.WIDTH))

    def rows(self):
        """Returns the rows."""
        return (self.row(i) for i in range(Game.HEIGHT))

    def update(self, location, new_tile):
        """@return a new Board equal to this board everywhere except
        at @p location, where @new_tile has replaced the prior value."""
        assert(self[location] == 0)
        (x, y) = location
        new_cols = copy.deepcopy(self._cols)
        new_cols[x][y] = new_tile
        return Board(new_cols)

    def rotate_cw(self):
        """Rotates a rectangular list of lists 'clockwise' (assuming
        board[x][y] is laid out in screen coordinates, ie with x
        increasing right and y increasing down)."""
        return Board(list(reversed(list_zip(*self._cols))))

    def rotate_ccw(self):
        """Rotates a rectangular list of lists 'counterclockwise'
        (assuming board[x][y] is laid out in screen coordinates, ie with x
        increasing right and y increasing down)."""
        return Board(list(list_zip(*reversed(self._cols))))

    def can_smash_up(self, column):
        changed, _, _ = self.smash_col_up(column)

    def smash_col_up(self, column):
        """Smashes a single column upward.  Returns (changed?, score, column)
        with the score incurred by the move and the new value of the
        column."""
        score = 0
        old_col = list(column)
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
        return (new_col != column, score, new_col)

    def smash_up(self):
        """As when one presses the 'up'-arrow in the game: Shifts all
        columns upward to the extent possible by combining pairs of
        like tiles.  Assumes a self in screen coordinate style.

        Returns (changed, score, new_cols) -- whether the smash changed
        anything, the score of this move (the total value of all tiles
        created) and the new board resulting."""
        score = 0
        new_cols = []
        changed = False
        for col in self._cols:
            col_changed, col_score, new_col = self.smash_col_up(col)
            changed |= col_changed
            score += col_score
            new_cols.append(new_col)
        return (changed, score, Board(new_cols))

    def can_move(self):
        """Return True if there are any moves on this board."""
        if any(cell == 0 for column in self._cols for cell in column):
            return True
        for col in self.columns():
            col = list(col)
            for i in range(Game.HEIGHT - 1):
                if col[i] == col[i + 1]: return True
        for row in self.rows():
            row = list(row)
            for i in range(Game.WIDTH - 1):
                if row[i] == row[i + 1]: return True
        return False


class Game(object):
    """A class representing a game in progress.  Also contains some public
    static constants of use to other classes."""

    WIDTH = 4
    HEIGHT = 4
    STARTING_TILES = [2, 2]
    TILE_FREQ = [(2, 0.75), (4, 0.25)]
    PRETTY_PRINT = {0: ' ', 2: '2', 4: '4', 8: '8',
                    16: 'A', 32: 'B', 64: 'C', 128: 'D',
                    256: 'E', 512: 'F', 1024: 'G',
                    2048: 'H', 4096: 'I', 8192: 'J'}

    # Allowable moves
    DIRECTIONS = UP, LEFT, DOWN, RIGHT = range(4)

    # Turn outcomes
    TURN_OUTCOMES = OK, ILLEGAL, GAMEOVER = range(3)

    def __init__(self, board=None, rnd=None, score=0):
        self._rnd = rnd if rnd is not None else random.Random()
        self._board = Board()
        self._score = score
        for t in Game.STARTING_TILES:
            self.add_tile(t)

    def __repr__(self):
        return ("Game(" + self._board + ", " +
                self._rnd.getstate() + ", " + self._score + ")")

    def prettyprint(self):
        print(self._score)
        self._board.prettyprint()

    def board(self):
        return self._board

    def score(self):
        return self._score

    def add_tile(self, tile_value=None):
        open_spaces = {(x, y)
                       for y in range(Game.HEIGHT)
                       for x in range(Game.WIDTH)
                       if not self._board[(x, y)]}
        if not open_spaces:
            return False
        r = self._rnd.random()
        if tile_value is None:
            for (tile, freq) in Game.TILE_FREQ:
                tile_value = tile
                if r < freq:
                    break
                else:
                    r -= freq
        (new_x, new_y) = self._rnd.sample(open_spaces, 1)[0]
        self._board = self._board.update((new_x, new_y), tile_value)
        return True

    def smash_without_counterrotate(self, direction):
        """Smashes in the given direction, leaving the board rotated
        with direction pointed up.  Returns True iff the smash actually
        changed anything other than the rotation."""
        new_board = copy.deepcopy(self._board)
        for _ in range(direction):
            new_board = new_board.rotate_cw()
        (changed, turn_score, new_board) = new_board.smash_up()
        if not changed:
            return False  # Illegal move
        self._score += turn_score
        self._board = new_board
        return True

    def smash(self, direction):
        changed = self.smash_without_counterrotate(direction)
        new_board = self._board
        for _ in range(direction):
            new_board = new_board.rotate_ccw()
        self._board = new_board
        return changed

    def do_turn(self, direction):
        smashed = self.smash(direction)
        if not smashed:
            # print "ILLEGAL MOVE"  # Verbosity for debugging
            return Game.ILLEGAL
        added = self.add_tile()
        if added:
            # self.prettyprint()  # Verbosity for debugging
            if self._board.can_move():
                return Game.OK
            else:
                return Game.GAMEOVER
        else:
            # print "GAME OVER"  # Verbosity for debugging
            return Game.GAMEOVER
