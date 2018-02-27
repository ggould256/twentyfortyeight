import argparse
import os
import sys

import keras as k
import numpy as np

from game.board import Board
from game.common import *
from strategy.nn.data import Dataset, EXAMPLE_WIDTH, MAX_TILE


HPARAMS = {"conv_channels": 30,
           "dense_sizes": [100, 50, 25],
           }

# Note:  Throughout, 'x' refers to the complete set of training data, 'y'
# to the corresponding scores to be predicted.


def _shuffle_in_unison(*arrays):
    rng_state = np.random.get_state()
    for array in arrays:
        np.random.set_state(rng_state)
        np.random.shuffle(array)


def make_model():
    raw_data = k.layers.Input(name="input",
                              shape=(EXAMPLE_WIDTH, MAX_TILE),
                              dtype='float32')
    print("Input X has shape", raw_data.shape)
    board = k.layers.Reshape(name="board",
                             target_shape=(HEIGHT, WIDTH, MAX_TILE),
                             )(raw_data)
    print("Board (into convolutional layers) has shape", board.shape)
    h_conv = k.layers.Conv2D(name="h_conv",
                             filters=HPARAMS["conv_channels"],
                             kernel_size=(4, 1),
                             activation="relu"
                             )(board)
    h_conv_reshaped = k.layers.Reshape((HEIGHT * HPARAMS["conv_channels"],)
                                       )(h_conv)
    print("Horiz. convolutional output has shape", h_conv.shape,
          "reshaped to", h_conv_reshaped.shape)
    v_conv = k.layers.Conv2D(name="v_conv",
                             filters=HPARAMS["conv_channels"],
                             kernel_size=(1, 4),
                             activation="relu",
                             )(board)
    v_conv_reshaped = k.layers.Reshape((WIDTH * HPARAMS["conv_channels"],)
                                       )(v_conv)
    print("Vert. convolutional output has shape", v_conv.shape,
          "reshaped to", v_conv_reshaped.shape)
    convs = k.layers.Concatenate()([h_conv_reshaped, v_conv_reshaped])
    print("Shape from convs into densors is", convs.shape)
    previous_output = convs
    # noinspection PyTypeChecker
    for i in range(len(HPARAMS["dense_sizes"])):
        previous_output = k.layers.Dense(units=HPARAMS["dense_sizes"][i],
                                         activation="relu",
                                         name=("dense_%s" % i))(previous_output)
        print("  Shape after densor", i, "is", previous_output.shape)
    result = k.layers.Dense(units=1,
                            activation="relu",
                            name="output")(previous_output)
    print("Output has shape", result.shape)
    return k.Model(inputs=raw_data, outputs=result)


def get_training_data(filename):
    """@returns x, x_as_onehot, y where x is a matrix of (example, tiles) and
    x_as_onehot is a tensor of (example, board position, onehot encoded tile)
    and y is a column vector of scores."""
    dataset = Dataset.load(filename)
    dataset.collapse()
    x_as_tiles = dataset.example_batches()[0]
    m, board_size = x_as_tiles.shape
    assert board_size == 16
    y = dataset.score_batches()[0]
    assert y.shape == (m,)
    # NOTE:  That Keras `to_categorical` retains the source dimensionality
    # of a multidimensional input as its leading axes is observed true but
    # not documented, and may be false in some versions/platforms!
    x_as_onehot = k.utils.to_categorical(x_as_tiles, MAX_TILE)
    assert(x_as_onehot.shape == (m, board_size, MAX_TILE))  # See NOTE above.
    _shuffle_in_unison(x_as_tiles, x_as_onehot, y)
    return x_as_tiles, x_as_onehot, y


def train_model(model, x, y, model_filename, num_epochs):
    model.compile(loss='mean_squared_error',
                  optimizer='Adam',
                  metrics=['mae'])
    model.fit(x, y, epochs=num_epochs, verbose=1)
    model.save(model_filename)


def show_exemplar(model, x, x_as_onehot, y):
    """Picks a random example from the data."""
    i = np.random.randint(0, x.shape[0])
    example = x[i,:]
    example_as_onehot = x_as_onehot[i]
    score = y[i]
    example_as_single_example = np.reshape(example_as_onehot,
                                           (1, WIDTH * HEIGHT, MAX_TILE))
    prediction = model.predict(example_as_single_example)

    # Encoding this back into a board requires some reformatting.
    tile_values = [0 if int(tile) == 0 else int(2 ** tile) for tile in example]
    board = Board([[tile_values[col * 4 + row] for col in range(4)]
                   for row in range(4)])

    board.pretty_print()
    print("Actual score: %d; predicted score: %s" % (score, prediction))


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--training_data', metavar='FILENAME', type=str,
                        help='npz file containing training data')
    parser.add_argument('--model_file', metavar='FILENAME', type=str,
                        help='keras model file to read in or output into')
    parser.add_argument('--epochs', type=int, help="number of training epochs",
                        default=5)
    args = parser.parse_args(argv[1:])

    x, x_as_onehot, y = get_training_data(args.training_data)
    if os.path.isfile(args.model_file):
        print("Loading existing model from", args.model_file)
        model = k.models.load_model(args.model_file)
    else:
        print("Training new model into", args.model_file)
        model = make_model()
        train_model(model, x_as_onehot, y, args.model_file, args.epochs)
    for i in range(5):
        show_exemplar(model, x, x_as_onehot, y)

if __name__ == '__main__':
    main(sys.argv)
