#!/usr/bin/env python3

"""Classes and functions related to dataset generation for learning Q
functions.  Datasets in this sense are mappings from board positions
(represented as flattened arrays of tile numbers) to score values.
"""

import argparse
import sys

import numpy as np

from game.common import *
from game.board import Board
from game.game import Game

EXAMPLE_WIDTH = Board.vector_width()
MAX_BATCH_SIZE = 4096  # numpy arrays get slow to update beyond this size.

class Dataset(object):
    """A set of training data (held as matrices whose rows are examples) and a
    column vector of the example scores.."""

    def __init__(self):
        """Creates a new empty dataset."""
        self._num_examples = 0
        self._example_batches = [np.zeros((0, EXAMPLE_WIDTH))]
        self._score_batches = [np.zeros((0, 1))]

    def add_game(self, player_strategy, rnd, starting_game_position=None):
        """Runs a game with the given strategy and randomness source, then
        enrolls the outcome in the dataset.

        If @p starting_position is a Game object, start from that position.

        Returns the number of examples (moves) added.
        """
        states = np.zeros((1, EXAMPLE_WIDTH))
        num_moves = 0
        game = starting_game_position or Game(rnd=rnd)
        running = True
        while running:
            intermediate_board, turn_outcome = (
                game.do_turn_and_retrieve_intermediate(
                    player_strategy.get_move(game.board(), game.score())))
            running = (turn_outcome != GAMEOVER)
            num_moves += (turn_outcome != ILLEGAL)
            if turn_outcome == OK:
                states = np.append(states,
                                   Board.as_vector(intermediate_board),
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

    def add_n_examples(self, strategy, rnd, n,
                       starting_positions_dataset=None):
        """Runs games and adds them to the dataset until at least @p n
        examples have been added.  Returns the number of examples added.

        If @p starting_positions_dataset is set, games will be started from
        a randomly selected position from that dataset rather than from a
        blank board."""
        print("Adding", n, "examples to dataset.")
        added = 0
        while added < n:
            starting_game = None
            if starting_positions_dataset:
                random_position = starting_positions_dataset.nth_example(
                    rnd.randint(0,
                                starting_positions_dataset.num_examples() - 1))
                starting_game = Game(Board.from_vector(random_position))
                if not starting_game.board().can_move():
                    continue
            num_added = self.add_game(strategy, rnd, starting_game)
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
    parser.add_argument('--strategy', metavar='FILE_OR_NAME', type=str,
                        help="name of strategy or filename of model",
                        default="random")
    parser.add_argument('--starting_positions', metavar='FILENAME', type=str,
                        default=None,
                        help=("If set, start some or all games from positions"
                              "drawn from this dataset"))
    parser.add_argument('--new_start_fraction', metavar='FRACTION', type=float,
                        default=1.,
                        help=("If --starting_positions is set, start this "
                              "fraction of games from a new game position"))
    args = parser.parse_args(argv[1:])

    import random
    from strategy.basic import RandomStrategy, SpinnyStrategy
    from strategy.nn.nn_strategy import ModelStrategy

    if args.strategy == "spinny":
        strategy = SpinnyStrategy()
    elif args.strategy == "random":
        strategy = RandomStrategy()
    else:
        strategy = ModelStrategy(args.strategy)

    start_positions_dataset = None
    if args.starting_positions:
        start_positions_dataset = Dataset.load(args.starting_positions)

    dataset = Dataset()
    num_added = dataset.add_n_examples(
        strategy, random, args.num_examples * args.new_start_fraction)
    if args.new_start_fraction < 1:
        assert start_positions_dataset, \
               "--new_start_fraction requires --starting_positions"
        num_added = dataset.add_n_examples(
            strategy, random, args.num_examples * (1 - args.new_start_fraction),
            starting_positions_dataset=start_positions_dataset)
    print("Added", num_added, "examples")
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
