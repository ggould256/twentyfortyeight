import keras as k
import numpy as np

from game.common import *
from strategy.nn.data import MAX_TILE, board_as_vector
from strategy.strategy import Strategy


class ModelStrategy(Strategy):
    def __init__(self, model_filename):
        self._model = k.models.load_model(model_filename)

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

    def get_move(self, board, score):
        best_dir = None
        best_score = float('-inf')
        for direction in DIRECTIONS:
            score = self._direction_prediction(board, direction)
            if score > best_score:
                best_score = score
                best_dir = direction
        return best_dir
