#!/usr/bin/env python3

"""Classes and functions related to dataset generation for learning Q
functions.  Datasets in this sense are mappings from board positions
(represented as long onehot-encoded arrays in the conventional fashion) to
score values.
"""

from rules import Game
import numpy as np

ENCODING_WIDTH = 16

def onehot(i, n=ENCODING_WIDTH):
    """Returns a vector of @p n elements, all zero except for the
    @p i th element, which will be 1."""
    result = np.zeros((1, n))
    result[(0,i)] = 1
    return result

class Dataset(object):
    """A set of training data, held as a matrix whose rows are examples and a
    column vector of the example scores.."""

    def __init__(self):
        """Creates a new empty dataset."""
        self._num_examples = 0
        self._example_width = ENCODING_WIDTH * Game.WIDTH * Game.HEIGHT
        self._examples = np.zeros((0, self._example_width))
        self._scores = np.zeros((0,1))

    ONEHOT_ENCODING = {0: onehot(0), 2: onehot(1), 4: onehot(2),
                       8: onehot(3), 16: onehot(4), 32: onehot(5),
                       64: onehot(6), 128: onehot(7), 256: onehot(8),
                       512: onehot(9), 1024: onehot(10), 2048: onehot(11),
                       4096: onehot(12), 8192: onehot(13)}

    def board_as_vector(self, board):
        """@return the contents of the given board as a row vector."""
        result = np.zeros((1,0))
        for column in board.columns():
            for cell in column:
                result = np.append(result, self.ONEHOT_ENCODING[cell], axis=1)
        assert(result.shape == (1, self._example_width))
        return result

    def add_game(self, strategy, rnd):
        """Runs a game with the given strategy and randomness source, then
        enrolls the outcome in the dataset.

        Returns the number of examples (moves) added.
        """
        states = np.zeros((1, self._example_width))
        num_moves = 0
        game = Game(rnd=rnd)
        running = True
        while running:
            intermediate_board, turn_outcome = (
                game.do_turn_and_retrieve_intermediate(
                    strategy.get_move(game.board(), game.score())))
            running = (turn_outcome != Game.GAMEOVER)
            num_moves += (turn_outcome != Game.ILLEGAL)
            if turn_outcome == Game.OK:
                states = np.append(states,
                                   self.board_as_vector(intermediate_board),
                                   axis=0)
                self._num_examples += 1
        strategy.notify_outcome(game.board(), game.score())

        scores = self.evaluate_states(states, game.board(), game.score)
        assert(len(states) == len(scores))
        self._examples = np.append(self._examples, states, axis=0)
        self._scores = np.append(self._scores, scores)
        return len(states)

    def evaluate_states(self, states, end_board, end_score):
        """Associate a Q score with each state of the current game.  There are
        many possible designs here, ranging from applying the ultimate score or
        highest attained tile to all of the states to scoring each state with
        the number of moves remainign in its game.  The correct function is
        not obvious; the current implementation is moves-remaining."""
        return np.array(list(range(len(states), 0, -1)))

    def add_n_examples(self, strategy, rnd, n):
        """Runs games and adds them to the dataset until at least @p n
        examples have been added.  Returns the number of examples added."""
        added = 0
        while added < n:
            added += self.add_game(strategy, rnd)
        return added

    def num_examples(self): return self._num_examples
    def example_width(self): return self._example_width
    def examples(self): return self._examples
    def scores(self): return self._scores



if __name__ == '__main__':
    import strategy
    import random
    strat = strategy.RandomStrategy()
    dataset = Dataset()
    num_added = dataset.add_n_examples(strat, random, 1e5)
    print("Added", num_added, "examples")
    print("Shapes:  X is", dataset.examples().shape,
          "Y is", dataset.scores().shape)
    print("Representative line ", dataset.examples()[10])
    print("Has score ", dataset.scores()[10])
    print("Representative line ", dataset.examples()[100])
    print("Has score ", dataset.scores()[100])
    print("Representative line ", dataset.examples()[1000])
    print("Has score ", dataset.scores()[1000])
