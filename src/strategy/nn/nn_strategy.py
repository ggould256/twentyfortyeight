import keras as k
import numpy as np

from game.common import *
from strategy.nn.data import MAX_TILE, board_as_vector
from strategy.strategy import Strategy


class ModelStrategy(Strategy):
    def __init__(self, model_filename, verbose_period=None):
        """Create a ModelStrategy reading the neural network from the given
        @p model_filename hdf5 file.  For debugging, output the board state
        every @p verbose_period moves (leave None for no verbosity)"""
        self._model = k.models.load_model(model_filename)
        self._verbosity = verbose_period or float("inf")
        self._count = 0


    def _direction_prediction(self, board, direction):
        for _ in range(direction):
            board = board.rotate_cw()
        changed, _, board = board.smash_up()
        if not changed:
            return float('-inf')  # illegal move
        as_vector = board_as_vector(board)
        as_onehot = k.utils.to_categorical(as_vector, MAX_TILE)
        example_as_single_example = np.reshape(as_onehot,
                                               (1, WIDTH * HEIGHT, MAX_TILE))
        return self._model.predict(example_as_single_example)

    def get_move(self, board, _):
        self._count += 1
        best_dir = None
        best_score = float('-inf')
        for direction in DIRECTIONS:
            score = self._direction_prediction(board, direction)
            if score > best_score:
                best_score = score
                best_dir = direction
        if self._count >= self._verbosity:
            print("Considering board:")
            board.pretty_print()
            print("the model chooses move", PRETTY_DIRECTION[best_dir],
                  "with score", best_score)
            self._count = 0
        return best_dir
