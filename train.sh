#!/bin/bash

# Train our first generation model.  It doesn't need much data because
# it is basically very, very stupid (and its input data is nearly random).
#
# Since all our data is generated, the only reason to use more than one
# epoch is that training is faster than generation.  But don't use very
# many epochs:  Training reaches a plateau very quickly, and I have taken
# no measures to avoid overfitting.
#
# Expect training to take about five minutes and end up with a mean error
# around 23.  The random strategy on a fairly random game makes it hard to
# predict outcomes with any certainty.
python3 -m strategy.nn.data --num_examples 500000 --output_file random_strategy_dataset.npz
python3 -m strategy.nn.model --training_data random_strategy_dataset.npz --model_file model.hdf5

