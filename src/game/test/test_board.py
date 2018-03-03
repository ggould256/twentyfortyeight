import unittest

from game.board import Board
from game.common import *


class TestBoard(unittest.TestCase):

    def setUp(self):
        # A board that's easy to read for debugging purposes but does
        # not have real tiles and so will fail smash/encode operations.
        self.readable_board = Board(
            [["00", "01", "02", "03"], ["10", "11", "12", "13"],
             ["20", "21", "22", "23"], ["30", "31", "32", "33"]])
        # A board that occurred in real play.
        self.realistic_board = Board(
            [[   2, 128,   8,   8],
             [   8,   8,  16,   0],
             [   4,  32,   4,   0],
             [   2,   4,   0,   0]])


    def test_smoke(self):
        board = Board()
        self.assertIsNotNone(board)

    def test_get(self):
        self.assertEqual(self.readable_board[1, 0], "10")
        self.assertEqual(self.readable_board[0, 2], "02")
        self.assertEqual(self.readable_board[3, 3], "33")

    def test_column(self):
        self.assertEqual(list(self.readable_board.column(0)),
                         ["00", "01", "02", "03"])

    def test_row(self):
        self.assertEqual(list(self.readable_board.row(0)),
                         ["00", "10", "20", "30"])

    def test_columns(self):
        self.assertEqual(list(self.readable_board.columns()),
                         [list(self.readable_board.column(i))
                          for i in range(WIDTH)])

    def test_rows(self):
        self.assertEqual(list(self.readable_board.rows()),
                         [list(self.readable_board.row(i))
                          for i in range(WIDTH)])

    def test_copy_and_update(self):
        original = self.readable_board
        copy = original.copy()
        self.assertIs(original, self.readable_board)
        self.assertIsNot(original, copy)
        self.assertEqual(original, copy)
        changed = copy.update([1, 2], "Wibble!")
        self.assertIsNot(changed, copy)
        self.assertNotEqual(changed, copy)
        self.assertEqual(changed[1, 2], "Wibble!")

    def test_rotate_cw(self):
        rotated = self.readable_board.rotate_cw()
        self.assertEqual(self.readable_board[0, 1], rotated[2, 0])

    def test_rotate_ccw(self):
        rotated = self.readable_board.rotate_ccw()
        self.assertEqual(self.readable_board[0, 1], rotated[1, 3])

    def test_rotate_against_rotate(self):
        self.assertEqual(self.readable_board,
                         self.readable_board.rotate_ccw().
                         rotate_ccw().rotate_ccw().rotate_ccw())
        self.assertEqual(self.readable_board.rotate_cw(),
                         self.readable_board.rotate_ccw().
                         rotate_ccw().rotate_ccw())
        self.assertEqual(self.readable_board.rotate_cw().rotate_cw(),
                         self.readable_board.rotate_ccw().rotate_ccw())
        self.assertEqual(self.readable_board.rotate_cw().rotate_cw().
                         rotate_cw(),
                         self.readable_board.rotate_ccw())
        self.assertEqual(self.readable_board.rotate_cw().rotate_cw().
                         rotate_cw().rotate_cw(),
                         self.readable_board)

    def test_can_smash(self):
        self.assertFalse(Board.can_smash_up([0, 0, 0, 0]))
        self.assertFalse(Board.can_smash_up([1, 0, 0, 0]))
        self.assertFalse(Board.can_smash_up([1, 2, 0, 0]))
        self.assertTrue(Board.can_smash_up([1, 1, 0, 0]))
        self.assertTrue(Board.can_smash_up([0, 1, 0, 0]))

    def test_smash_col(self):
        self.assertEqual(Board.smash_col_up([0, 0, 0, 0]),
                         (False, 0, [0, 0, 0, 0]))
        self.assertEqual(Board.smash_col_up([1, 0, 0, 0]),
                         (False, 0, [1, 0, 0, 0]))
        self.assertEqual(Board.smash_col_up([1, 2, 0, 0]),
                         (False, 0, [1, 2, 0, 0]))
        self.assertEqual(Board.smash_col_up([1, 1, 0, 0]),
                         (True, 2, [2, 0, 0, 0]))
        self.assertEqual(Board.smash_col_up([0, 1, 0, 0]),
                         (True, 0, [1, 0, 0, 0]))

    def test_smash_and_can_move(self):
        # Empty board does not move.
        board = Board()
        self.assertFalse(board.can_move())
        changed, score, smashed = board.smash_up()
        self.assertFalse(changed)
        self.assertEqual(score, 0)
        self.assertEqual(smashed, Board())
        self.assertIsNot(smashed, board)
        # Board with a floating tile slides that tile.
        board = board.update([1, 2], 1)
        self.assertTrue(board.can_move())
        changed, score, smashed = board.smash_up()
        self.assertTrue(changed)
        self.assertEqual(score, 0)
        self.assertNotEqual(smashed, board)
        self.assertEqual(smashed, Board().update([1, 0], 1))
        # Board with aligned tiles smashes those tiles.
        board = board.update([1, 0], 1)
        self.assertTrue(board.can_move())
        changed, score, smashed = board.smash_up()
        self.assertTrue(changed)
        self.assertEqual(score, 2)
        self.assertNotEqual(smashed, board)
        self.assertEqual(smashed, Board().update([1, 0], 2))
        # Locked board does not move.
        board = Board([[1, 2, 1, 2], [2, 1, 2, 1],
                       [1, 2, 1, 2], [2, 1, 2, 1]])
        self.assertFalse(board.can_move())
        changed, score, smashed = board.smash_up()
        self.assertFalse(changed)
        self.assertEqual(score, 0)
        self.assertEqual(smashed, board)
        self.assertIsNot(smashed, board)

    def test_encoding(self):
        board = self.realistic_board
        encoding = board.as_vector()
        self.assertEqual(encoding.size, Board.vector_width())
        decoding = Board.from_vector(encoding)
        self.assertEqual(board, decoding)


if __name__ == '__main__':
    unittest.main()
