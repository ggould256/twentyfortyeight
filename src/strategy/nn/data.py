#!/usr/bin/env python3

"""Classes and functions related to dataset generation for learning Q
functions.  Datasets in this sense are mappings from board positions
(represented as flattened arrays of tile numbers) to score values.
"""

import numpy as np

from game.common import *
from game.game import Game
from strategy.basic import RandomStrategy

ENCODING_WIDTH = 1
MAX_BATCH_SIZE = 4096  # numpy arrays get slow to update beyond this size.
EXAMPLE_WIDTH = ENCODING_WIDTH * WIDTH * HEIGHT


class Dataset(object):
    """A set of training data, held as matrices whose rows are examples and a
    column vector of the example scores.."""

    def __init__(self):
        """Creates a new empty dataset."""
        self._num_examples = 0
        self._example_batches = [np.zeros((0, EXAMPLE_WIDTH))]
        self._score_batches = [np.zeros((0, 1))]

    ENCODING = {**{0: np.array([[0]])},
                **{2**n: np.array([[n]]) for n in range(1, 15)}}

    def board_as_vector(self, board):
        """@return the contents of the given board as a row vector."""
        result = np.zeros((1, 0))
        for column in board.columns():
            for cell in column:
                result = np.append(result, self.ENCODING[cell], axis=1)
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
            self._score_batches.append(np.zeros((0, 1)))
        self._example_batches[-1] = \
            np.append(self._example_batches[-1], states, axis=0)
        self._score_batches[-1] = np.append(self._score_batches[-1], scores)
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

    def num_batches(self):
        return len(self._example_batches)

    def num_examples(self):
        return self._num_examples

    def example_batches(self):
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

    def nth_score(self, n):
        counter = n
        for batch in self._score_batches:
            size = batch.shape[0]
            if counter < size:
                return batch[counter]
            else:
                counter -= size
        return None

    def score_batches(self):
        return self._score_batches


def test_with_random():
    import random
    strategy = RandomStrategy()
    dataset = Dataset()
    num_added = dataset.add_n_examples(strategy, random, 1e5)
    print("Added", num_added, "examples")
    for index in range(dataset.num_batches()):
        print("X shape is %s, Y shape is %s" %
              (dataset.example_batches()[index].shape,
               dataset.score_batches()[index].shape))
    print("Representative line ", dataset.nth_example(10))
    print("Has score ", dataset.nth_score(10))
    print("Representative line ", dataset.nth_example(100))
    print("Has score ", dataset.nth_score(100))
    print("Representative line ", dataset.nth_example(1000))
    print("Has score ", dataset.nth_score(1000))
    print("Representative line ", dataset.nth_example(10000))
    print("Has score ", dataset.nth_score(10000))


if __name__ == '__main__':
    test_with_random()
