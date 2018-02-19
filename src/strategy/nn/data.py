#!/usr/bin/env python3

"""Classes and functions related to dataset generation for learning Q
functions.  Datasets in this sense are mappings from board positions
(represented as flattened arrays of tile numbers) to score values.
"""

import argparse
import sys

import numpy as np

from game.common import *
from game.game import Game
from strategy.basic import RandomStrategy

ENCODING_WIDTH = 1
MAX_BATCH_SIZE = 4096  # numpy arrays get slow to update beyond this size.
EXAMPLE_WIDTH = ENCODING_WIDTH * WIDTH * HEIGHT
MAX_TILE = 15
ENCODING = {**{0: np.array([[0]])},
            **{2 ** n: np.array([[n]]) for n in range(1, MAX_TILE)}}


def board_as_vector(board):
    """@return the contents of the given board as a row vector."""
    result = np.zeros((1, 0))
    for column in board.columns():
        for cell in column:
            result = np.append(result, ENCODING[cell], axis=1)
    assert (result.shape == (1, EXAMPLE_WIDTH))
    return result


class Dataset(object):
    """A set of training data (held as matrices whose rows are examples) and a
    column vector of the example scores.."""

    def __init__(self):
        """Creates a new empty dataset."""
        self._num_examples = 0
        self._example_batches = [np.zeros((0, EXAMPLE_WIDTH))]
        self._score_batches = [np.zeros((0, 1))]

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
                                   board_as_vector(intermediate_board),
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
            if (added // 10000) != ((num_added + added) // 10000):
                print("Added %d so far..." % (num_added + added))
            added += num_added
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

    def collapse(self):
        """Collapses all of the batches down to a single, very large batch."""
        self._score_batches = [np.concatenate(self._score_batches)]
        self._example_batches = [np.concatenate(self._example_batches)]

    def save(self, filename):
        assert(filename.endswith(".npz"))
        num_batches = len(self._example_batches)
        examples_dict = {"examples_%s" % i: self._example_batches[i]
                         for i in range(num_batches)}
        scores_dict = {"scores_%s" % i: self._score_batches[i]
                       for i in range(num_batches)}
        unified_dict = {**examples_dict, **scores_dict}
        with open(filename, "wb") as f:
            np.savez(f, **unified_dict)

    @staticmethod
    def load(filename):
        assert(filename.endswith(".npz"))
        with open(filename, "rb") as f:
            npz_data = np.load(f)
            data = Dataset()
            data._example_batches = []
            data._score_batches = []
            num_batches = len(npz_data.files) // 2
            for i in range(num_batches):
                data._example_batches.append(
                    npz_data["examples_%s" % i])
                data._score_batches.append(
                    npz_data["scores_%s" % i])
            data._num_examples = sum(array.shape[0]
                                     for array in data._example_batches)
            return data


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_examples', metavar='N', type=int,
                        help="Number of examples (at minimum) to generate")
    parser.add_argument('--output_file', metavar='FILENAME', type=str,
                        help="npz file into which to write example data")
    args = parser.parse_args(argv[1:])

    import random
    strategy = RandomStrategy()
    dataset = Dataset()
    num_added = dataset.add_n_examples(strategy, random, args.num_examples)
    print("Added", num_added, "examples")
    for index in range(dataset.num_batches()):
        print("X shape is %s, Y shape is %s" %
              (dataset.example_batches()[index].shape,
               dataset.score_batches()[index].shape))
    print("saving...")
    dataset.save(args.output_file)
    print("...saved.")
    print("checking output file validity...")
    check_data = Dataset.load(args.output_file)
    assert dataset.num_batches() == check_data.num_batches(), \
        ("original batch number %s does not equal output batch number %s"
         % (dataset.num_batches(), check_data.num_batches()))
    check_data.collapse()
    print("...output is valid.")


if __name__ == '__main__':
    main(sys.argv)
