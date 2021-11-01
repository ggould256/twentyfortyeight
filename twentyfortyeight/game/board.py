import copy

import numpy as np

from .common import WIDTH, HEIGHT, list_zip, PRETTY_PRINT


ENCODING_WIDTH = 1
EXAMPLE_WIDTH = ENCODING_WIDTH * WIDTH * HEIGHT
MAX_TILE = 15
ENCODING = {**{0: np.array([[0]])},
            **{2 ** n: np.array([[n]]) for n in range(1, MAX_TILE)}}


class Board(object):
    """An immutable class representing an arrangement of tiles on the game
    board.
    """
    def __init__(self, cols_data=None):
        if cols_data is None:
            self._cols = [[0 for _ in range(HEIGHT)]
                          for _ in range(WIDTH)]
        else:
            self._cols = [[cols_data[x][y] for y in range(HEIGHT)]
                          for x in range(WIDTH)]

    def __getitem__(self, location=None):
        """Allow indexing by coordinates, eg board[(x,y)]."""
        (x, y) = location
        return self._cols[x][y]

    def __eq__(self, other):
        return all(self._cols[i] == other.column(i)
                   for i in range(WIDTH))

    def pretty_print(self):
        print("+-" + ("--" * WIDTH) + "+")
        for y in range(HEIGHT):
            line = "| "
            for x in range(WIDTH):
                line += PRETTY_PRINT[self._cols[x][y]] + " "
            line += "|"
            print(line)
        print("+-" + ("--" * WIDTH) + "+")

    def column(self, x):
        """Returns the xth column."""
        return list(self._cols[x])

    def row(self, y):
        """Returns the yth row."""
        return (self._cols[x][y] for x in range(WIDTH))

    def columns(self):
        """Returns the columns."""
        return (list(self.column(i)) for i in range(WIDTH))

    def rows(self):
        """Returns the rows."""
        return (list(self.row(i)) for i in range(HEIGHT))

    def copy(self):
        return Board(copy.deepcopy(self._cols))

    def update(self, location, new_tile):
        """@return a new Board equal to this board everywhere except
        at @p location, where @new_tile has replaced the prior value."""
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

    @staticmethod
    def can_smash_up(column):
        changed, _, _ = Board.smash_col_up(column)
        return changed

    @staticmethod
    def smash_col_up(column):
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
        new_col += [0] * (HEIGHT - len(new_col))
        return (new_col != column), score, new_col

    def smash_up(self):
        """As when one presses the 'up'-arrow in the game: Shifts all
        columns upward to the extent possible by combining pairs of
        like tiles.  Assumes a self in screen coordinate style.

        Returns (changed, score, new_board) -- whether the smash changed
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
        return changed, score, Board(new_cols)

    def can_move(self):
        """Return True if there are any moves on this board."""
        if any(cell == 0 for column in self._cols for cell in column):
            return any(cell != 0 for column in self._cols for cell in column)
        for col in self.columns():
            col = list(col)
            for i in range(HEIGHT - 1):
                if col[i] == col[i + 1]:
                    return True
        for row in self.rows():
            row = list(row)
            for i in range(WIDTH - 1):
                if row[i] == row[i + 1]:
                    return True
        return False

    # Methods for serializing boards to and from numpy vectors, for storage
    # and use as neural network inputs.

    @staticmethod
    def vector_width():
        return ENCODING_WIDTH * WIDTH * HEIGHT

    def as_vector(self):
        """@return the contents of the given board as a row vector."""
        result = np.zeros((1, 0))
        for column in self.columns():
            for cell in column:
                result = np.append(result, ENCODING[cell], axis=1)
        assert (result.shape == (1, Board.vector_width()))
        return result

    @staticmethod
    def from_vector(vec):
        # Encoding this back into a board requires some reformatting.
        tile_values = [0 if int(tile) == 0 else int(2 ** tile)
                       for tile in vec.flatten()]
        board = Board([[tile_values[col * HEIGHT + row]
                        for row in range(HEIGHT)]
                       for col in range(WIDTH)])
        return board
