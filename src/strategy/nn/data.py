#!/usr/bin/env python3

"""Classes and functions related to dataset generation for learning Q
functions.  Datasets in this sense are mappings from board positions
(represented as long onehot-encoded arrays in the conventional fashion) to
score values.
"""

import numpy as np

from game.common import *
from game.game import Game
from strategy.basic import RandomStrategy

ENCODING_WIDTH = 16
MAX_BATCH_SIZE = 1024  # numpy arrays get slow to update beyond this size.
EXAMPLE_WIDTH = ENCODING_WIDTH * WIDTH * HEIGHT


def onehot(i, n=ENCODING_WIDTH):
    """Returns a vector of @p n elements, all zero except for the
    @p i th element, which will be 1."""
    result = np.zeros((1, n))
    result[0, i] = 1
    return result


class Dataset(object):
    """A set of training data, held as matrices whose rows are examples and a
    column vector of the example scores.."""

    def __init__(self):
        """Creates a new empty dataset."""
        self._num_examples = 0
        self._example_batches = [np.zeros((0, EXAMPLE_WIDTH))]
        self._scores = np.zeros((0, 1))

    ONEHOT_ENCODING = {0: onehot(0), 2: onehot(1), 4: onehot(2),
                       8: onehot(3), 16: onehot(4), 32: onehot(5),
                       64: onehot(6), 128: onehot(7), 256: onehot(8),
                       512: onehot(9), 1024: onehot(10), 2048: onehot(11),
                       4096: onehot(12), 8192: onehot(13)}

    def board_as_vector(self, board):
        """@return the contents of the given board as a row vector."""
        result = np.zeros((1, 0))
        for column in board.columns():
            for cell in column:
                result = np.append(result, self.ONEHOT_ENCODING[cell], axis=1)
        assert(result.shape == (1, EXAMPLE_WIDTH))
        return result

    def add_game(self, player_strategy, rnd):
        """Runs a game with the given strategy and randomness source, then
        enrolls the outcome in the dataset.

        Returns the number of examples (moves) added.
        """
        states = np.zeros((1, EXAMPLE_WIDTH))
        num_moves = 0
        game = Game(rnd=rnd)
        running = True
        while running:
            intermediate_board, turn_outcome = (
                game.do_turn_and_retrieve_intermediate(
                    player_strategy.get_move(game.board(), game.score())))
            running = (turn_outcome != GAMEOVER)
            num_moves += (turn_outcome != ILLEGAL)
            if turn_outcome == OK:
                states = np.append(states,
                                   self.board_as_vector(intermediate_board),
                                   axis=0)
                self._num_examples += 1
        player_strategy.notify_outcome(game.board(), game.score())

        scores = Dataset.evaluate_states(states, game.board(), game.score)
        assert(len(states) == len(scores))
        batch_size_so_far = self._example_batches[-1].shape[0]
        if len(states) + batch_size_so_far > MAX_BATCH_SIZE:
            self._example_batches.append(np.zeros((0, EXAMPLE_WIDTH)))
        self._example_batches[-1] = \
            np.append(self._example_batches[-1], states, axis=0)
        self._scores = np.append(self._scores, scores)
        return len(states)

    @staticmethod
    def evaluate_states(states, end_board, end_score):
        """Associate a Q score with each state of the current game.  There are
        many possible designs here, ranging from applying the ultimate score or
        highest attained tile to all of the states to scoring each state with
        the number of moves remaining in its game.  The correct function is
        not obvious; the current implementation is moves-remaining."""
        del end_board, end_score
        return np.array(list(range(len(states), 0, -1)))

    def add_n_examples(self, strategy, rnd, n):
        """Runs games and adds them to the dataset until at least @p n
        examples have been added.  Returns the number of examples added."""
        added = 0
        while added < n:
            num_added = self.add_game(strategy, rnd)
            added += num_added
            print("Added a game of %d moves; %d moves in dataset addition." %
                  (num_added, added))
        return added

    def num_examples(self):
        return self._num_examples

    def batches(self):
        return self._example_batches

    def nth_example(self, n):
        counter = n
        for batch in self._example_batches:
            size = batch.shape[0]
            if counter < size:
                return batch[counter, :]
            else:
                counter -= size
        return None

    def scores(self):
        return self._scores


def test_with_random():
    import random
    strategy = RandomStrategy()
    dataset = Dataset()
    num_added = dataset.add_n_examples(strategy, random, 1e5)
    print("Added", num_added, "examples")
    print("Shapes:  X is", [batch.shape for batch in dataset.batches()],
          "Y is", dataset.scores().shape)
    print("Representative line ", dataset.nth_example(10))
    print("Has score ", dataset.scores()[10])
    print("Representative line ", dataset.nth_example(100))
    print("Has score ", dataset.scores()[100])
    print("Representative line ", dataset.nth_example(1000))
    print("Has score ", dataset.scores()[1000])


if __name__ == '__main__':
    test_with_random()
