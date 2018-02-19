import argparse
import sys

import keras as k
import numpy as np

from game.common import *
from strategy.nn.data import Dataset, EXAMPLE_WIDTH, MAX_TILE


HPARAMS = {"conv_channels": 30,
           "dense_sizes": [200, 100, 50]
           }


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
    """@returns x, y where x is a tensor of
    (example, board position, onehot encoded tile)
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
    x = k.utils.to_categorical(x_as_tiles, MAX_TILE)
    assert(x.shape == (m, board_size, MAX_TILE))  # See NOTE above.
    np.random.shuffle(x)
    return x, y


def train_model(model, data_filename, model_filename):
    x, y = get_training_data(data_filename)
    model.compile(loss='mean_squared_error',
                  optimizer='Adam',
                  metrics=['mae'])
    model.fit(x, y, epochs=5, verbose=1)
    model.save(model_filename)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--training_data', metavar='FILENAME', type=str,
                        help='npz file containing training data')
    parser.add_argument('--output_file', metavar='FILENAME', type=str,
                        help='keras model file to output with trained model')
    args = parser.parse_args(argv[1:])
    model = make_model()
    train_model(model, args.training_data, args.output_file)


if __name__ == '__main__':
    main(sys.argv)
