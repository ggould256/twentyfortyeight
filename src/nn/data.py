#!/usr/bin/env python3

"""Classes and functions related to dataset generation for learning Q
functions.  Datasets in this sense are mappings from board positions
(represented as long onehot-encoded arrays in the conventional fashion) to
score values.
"""

from rules import Game

def onehot(i, n=16):
    """Returns a vector of @p n elements, all zero except for the
    @p i th element, which will be 1."""
    result = [0] * n
    result[i] = 1
    return result

class Dataset(object):
    """A set of training data."""

    def __init__(self):
        """Creates a new empty dataset."""
        self.examples = []
        self.scores = []

    ONEHOT_ENCODING = {0: onehot(0), 2: onehot(1), 4: onehot(2),
                       8: onehot(3), 16: onehot(4), 32: onehot(5),
                       64: onehot(6), 128: onehot(7), 256: onehot(8),
                       512: onehot(9), 1024: onehot(10), 2048: onehot(11),
                       4096: onehot(12), 8192: onehot(13)}

    def board_as_vector(self, board):
        """@return the contents of the given board as a flat vector."""
        result = []
        for column in board.columns():
            for cell in column:
                result += self.ONEHOT_ENCODING[cell]
        return result

    def add_game(self, strategy, rnd):
        """Runs a game with the given strategy and randomness source, then
        enrolls the outcome in the dataset.

        Returns the number of examples (moves) added.
        """
        states = []
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
                states += [self.board_as_vector(intermediate_board)]
        strategy.notify_outcome(game.board(), game.score())

        scores = self.evaluate_states(states, game.board(), game.score)
        assert(len(states) == len(scores))
        self.examples += states
        self.scores += scores
        return len(states)

    def evaluate_states(self, states, end_board, end_score):
        """Associate a Q score with each state of the current game.  There are
        many possible designs here, ranging from applying the ultimate score or
        highest attained tile to all of the states to scoring each state with
        the number of moves remainign in its game.  The correct function is
        not obvious; the current implementation is moves-remaining."""
        return list(range(len(states), 0, -1))

    def add_n_examples(self, strategy, rnd, n):
        """Runs games and adds them to the dataset until at least @p n
        examples have been added.  Returns the number of examples added."""
        added = 0
        while added < n:
            added += self.add_game(strategy, rnd)
        return added


if __name__ == '__main__':
    import strategy
    import random
    strat = strategy.RandomStrategy()
    dataset = Dataset()
    num_added = dataset.add_n_examples(strat, random, 1e6)
    print("Added", num_added, "examples")
